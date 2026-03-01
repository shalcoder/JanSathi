"""
connect_webhook.py – IVR / Amazon Connect Lambda entry point.

Delegates to JanSathiSupervisor for the full 9-agent pipeline:
  Telecom Entry → Intent → Slot/Rules → Verifier → Notify/HITL

Returns { "playPrompt", "sessionAttributes", "intent", "requiresInput" }
for Amazon Connect TTS.
"""

import logging
import os
import time
import uuid
from typing import Optional

from app.agent.supervisor import get_supervisor
from app.services.telemetry_service import get_telemetry

# Layer 1 & 9 Integration
from app.automation.l1_integration.schema import UnifiedEventObject
from app.automation.l9_observability.logger import get_structured_logger

logger = logging.getLogger(__name__)
struct_logger = get_structured_logger("JanSathiAutomation")


# ── Language helpers ────────────────────────────────────────────────────────

WELCOME_MESSAGES = {
    "hi": "नमस्ते! मैं जनसाथी हूँ। सहमति के लिए 1 दबाएँ।",
    "ta": "வணக்கம்! நான் ஜன் சாதி. சம்மதிக்க 1 அழுத்தவும்.",
    "en": "Hello! I am JanSathi. Press 1 to consent and continue.",
}

def _lang(language: str) -> str:
    return language[:2].lower() if language else "en"


# ── Main entry point ────────────────────────────────────────────────────────

def handle_connect_invocation(event: dict) -> dict:
    """
    Amazon Connect Lambda entry point — delegates to JanSathiSupervisor.

    event keys:
      contactId / Details.ContactData.ContactId  → session_id
      language        str   'hi'|'ta'|'en'
      text            str   pre-transcribed text
      audioS3Key      str   S3 key to transcribe
      audioS3Bucket   str   S3 bucket
      dtmfDigits      str   DTMF input
      consent         bool  True if user pressed 1
      sessionAttributes dict
    """
    t_start = time.perf_counter()
    tel = get_telemetry()

    contact_id = (
        event.get("contactId") or
        event.get("Details", {}).get("ContactData", {}).get("ContactId") or
        uuid.uuid4().hex[:8]
    )
    
    # ── [NEW] IVR Caller Profile Lookup ──
    # Look up profile by phone number (if available) to inject context
    caller_number = event.get("callerNumber", "")
    profile_context = {}
    if caller_number:
        try:
            from app.models.models import UserProfile
            import re
            # Normalize E.164 phone number
            clean_phone = re.sub(r'[^\d+]', '', caller_number)
            if clean_phone.startswith("0") and len(clean_phone) == 11:
                clean_phone = "+91" + clean_phone[1:]
            elif len(clean_phone) == 10 and not clean_phone.startswith("+"):
                clean_phone = "+91" + clean_phone
                
            from app.models.models import db
            # Need app context here since this is often run outside a request
            from flask import current_app
            if current_app:
                profile = UserProfile.query.filter_by(phone_e164=clean_phone).first()
                if profile:
                    profile_context = profile.to_ivr_context()
                    logger.info(f"[ConnectWebhook] Found profile for {clean_phone}: {profile_context.get('name')}")
        except Exception as e:
            logger.error(f"[ConnectWebhook] Profile lookup failed: {e}")

    session_id    = f"ivr-{contact_id}"
    language      = event.get("language", "hi")
    lang_key      = _lang(language)
    session_attrs = dict(event.get("sessionAttributes", {}))
    
    # Inject profile context into session attributes if not already present
    if profile_context and not session_attrs.get("profile_context"):
        import json
        session_attrs["profile_context"] = json.dumps(profile_context)

    consent       = event.get("consent", False)

    tel.emit("CallProcessed", 1.0, {"channel": "ivr", "language": lang_key})

    # ── Consent gate ───────────────────────────────────────────────────────
    if not consent:
        return _build_response(
            WELCOME_MESSAGES.get(lang_key, WELCOME_MESSAGES["en"]),
            session_attrs, "consent_required", language, requires_input=True
        )

    # ── Get transcript ─────────────────────────────────────────────────────
    transcript     = event.get("text", "").strip()
    asr_confidence = 1.0

    if not transcript:
        audio_key    = event.get("audioS3Key", "")
        audio_bucket = event.get("audioS3Bucket", os.getenv("AUDIO_BUCKET", ""))
        if audio_key and audio_bucket:
            try:
                from app.services.transcribe_service import TranscribeService
                raw = TranscribeService().transcribe_audio_s3(audio_bucket, audio_key, language)
                if isinstance(raw, dict):
                    transcript     = raw.get("transcript", "")
                    asr_confidence = float(raw.get("confidence", 0.8))
                else:
                    transcript     = str(raw)
                    asr_confidence = 0.8
                logger.info(f"[ConnectWebhook] ASR: '{transcript[:80]}' conf={asr_confidence:.2f}")
            except Exception as e:
                logger.error(f"[ConnectWebhook] Transcription failed: {e}")

    if not transcript:
        dtmf = event.get("dtmfDigits", "")
        if dtmf:
            transcript     = f"DTMF:{dtmf}"
            asr_confidence = 1.0

    tel.emit("ASRSuccessRate",
             100.0 if asr_confidence >= 0.6 else 0.0,
             {"channel": "ivr"}, unit="Percent")

    # ── [NEW Layer 1/9] Unified Event Object & Structured Logging ──
    unified_event = UnifiedEventObject(
        session_id=session_id,
        channel="ivr",
        language=language,
        message=transcript,
        user_context=profile_context,
        channel_metadata={"asr_confidence": asr_confidence, "slots": session_attrs},
        consent_given=consent
    )
    
    struct_logger.info("Telecom Voice Trigger Received", layer="1_Integration", session_id=session_id)
    struct_logger.info(f"Ingested utterance: '{transcript}'", layer="2_Ingestion", session_id=session_id)

    # Convert to dict for legacy compatibility while supervisor is refactored
    supervisor_event = {
        "session_id":     unified_event.session_id,
        "message":        unified_event.message,
        "language":       unified_event.language,
        "channel":        unified_event.channel,
        "consent":        unified_event.consent_given,
        "asr_confidence": unified_event.channel_metadata.get("asr_confidence", 1.0),
        "turn_id":        str(uuid.uuid4()),
        "slots":          {k: v for k, v in session_attrs.items() if not k.startswith("_")},
    }

    try:
        result = get_supervisor().orchestrate(supervisor_event)
    except Exception as e:
        logger.error(f"[ConnectWebhook] Supervisor error: {e}")
        result = {
            "play_prompt":    "क्षमा करें, एक समस्या हुई। कृपया पुनः प्रयास करें।",
            "requires_input": False,
            "intent":         "ERROR",
        }

    play_prompt = (
        result.get("play_prompt") or
        result.get("response_text") or
        "आपका अनुरोध प्रक्रिया में है।"
    )
    session_attrs.update({
        "intent":      result.get("intent", ""),
        "language":    language,
        "case_id":     result.get("case_id", ""),
        "receipt_url": result.get("receipt_url", ""),
        "session_id":  session_id,
        "latency_ms":  str(round((time.perf_counter() - t_start) * 1000, 2)),
    })

    return _build_response(
        play_prompt, session_attrs,
        result.get("intent", ""), language,
        requires_input=result.get("requires_input", False),
    )



# ──────────────────────────────────────────────────────────────────────────────
# Language helpers
# ──────────────────────────────────────────────────────────────────────────────

WELCOME_MESSAGES = {
    "hi": "नमस्ते! मैं जनसाथी हूँ। आपकी सरकारी योजनाओं में कैसे मदद कर सकता हूँ?",
    "ta": "வணக்கம்! நான் ஜன் சாதி. அரசு திட்டங்களில் உங்களுக்கு எப்படி உதவலாம்?",
    "en": "Hello! I am JanSathi. How can I help you with government schemes today?",
}

SLOT_COLLECT_INTROS = {
    "hi": "मैं आपके आवेदन के लिए कुछ जानकारी एकत्र करूंगा।",
    "ta": "விண்ணப்பத்திற்கு சில தகவல்கள் சேகரிக்கிறேன்.",
    "en": "I will collect a few details to complete your application.",
}

PROCESSING_MESSAGES = {
    "hi": "आपका अनुरोध प्रक्रिया में है। आपको SMS मिलेगा।",
    "ta": "உங்கள் கோரிக்கை செயலாக்கப்படுகிறது. SMS வரும்.",
    "en": "Your request is being processed. You will receive an SMS shortly.",
}

ERROR_MESSAGES = {
    "hi": "क्षमा करें, एक समस्या हुई। कृपया पुनः प्रयास करें।",
    "en": "I'm sorry, something went wrong. Please try again.",
}


def _lang(language: str) -> str:
    """Normalise language code to 2-letter key."""
    return language[:2].lower() if language else "en"


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────────

def handle_connect_invocation(event: dict) -> dict:
    """
    Primary handler for Amazon Connect Lambda invocations.

    Expected event keys (all optional, best-effort):
      contactId         str   – Connect contact ID (used as session_id)
      language          str   – 'hi', 'ta', 'en' etc.
      text              str   – Direct text transcript (if already transcribed)
      audioS3Key        str   – S3 key for audio file to transcribe
      audioS3Bucket     str   – S3 bucket for audio file
      dtmfDigits        str   – DTMF input (digits pressed by user)
      sessionAttributes dict  – Attributes carried forward from Connect flow

    Returns:
      {
        "playPrompt": str,           # Text for Connect TTS
        "sessionAttributes": dict,   # Attributes to persist in Connect
        "intent": str,               # Detected intent
        "language": str,             # Detected/confirmed language
        "requiresInput": bool        # Whether flow should wait for more input
      }
    """
    intent_svc, polly_svc, transcribe_svc = _get_services()

    contact_id = event.get("contactId", event.get("Details", {}).get("ContactData", {}).get("ContactId", "unknown"))
    session_id = f"ivr-{contact_id}"
    language = event.get("language", "hi")
    lang_key = _lang(language)
    session_attrs = event.get("sessionAttributes", {})

    # ── 1. Get transcript ─────────────────────────────────────────────────────
    transcript = event.get("text", "").strip()

    if not transcript:
        audio_key = event.get("audioS3Key", "")
        audio_bucket = event.get("audioS3Bucket", os.getenv("AUDIO_BUCKET", ""))
        if audio_key and audio_bucket:
            try:
                transcript = transcribe_svc.transcribe_audio_s3(audio_bucket, audio_key, language)
                logger.info(f"[ConnectWebhook] Transcribed: '{transcript[:80]}'")
            except Exception as e:
                logger.error(f"[ConnectWebhook] Transcription failed: {e}")

    # DTMF fallback
    if not transcript:
        dtmf = event.get("dtmfDigits", "")
        if dtmf:
            transcript = f"DTMF:{dtmf}"

    if not transcript:
        # Welcome / idle prompt
        prompt = WELCOME_MESSAGES.get(lang_key, WELCOME_MESSAGES["en"])
        return _build_response(prompt, session_attrs, "greeting", language, requires_input=True)

    # ── 2. Classify intent ────────────────────────────────────────────────────
    try:
        intent_result = intent_svc.classify_intent_ivr(transcript, language)
        intent = intent_result.get("intent", "info")
        confidence = intent_result.get("confidence", 0.8)
        language_detected = intent_result.get("language_detected", language)
        lang_key = _lang(language_detected)
    except Exception as e:
        logger.error(f"[ConnectWebhook] Intent classification failed: {e}")
        intent = "info"
        confidence = 0.5
        language_detected = language

    session_attrs.update({
        "intent": intent,
        "language": language_detected,
        "confidence": str(confidence),
    })

    logger.info(f"[ConnectWebhook] session={session_id} intent={intent} conf={confidence:.2f} lang={language_detected}")

    # ── 3. Route by intent ────────────────────────────────────────────────────

    if intent == "apply":
        return _handle_apply(session_id, transcript, lang_key, session_attrs, confidence)

    elif intent == "grievance":
        return _handle_grievance(session_id, transcript, lang_key, session_attrs, confidence)

    elif intent == "track":
        return _handle_track(session_id, lang_key, session_attrs)

    else:  # info / general_query / fallback
        return _handle_info(session_id, transcript, lang_key, polly_svc, session_attrs)


# ──────────────────────────────────────────────────────────────────────────────
# Intent handlers
# ──────────────────────────────────────────────────────────────────────────────

def _handle_apply(session_id, transcript, lang_key, session_attrs, confidence):
    """Route apply intent → workflow engine slot collection."""
    try:
        # Detect scheme from transcript (simple keyword match; Bedrock can improve this)
        scheme = _detect_scheme(transcript)
        session_attrs["scheme"] = scheme

        result = process_user_input(
            message=f"start_apply:{scheme}",
            session_id=session_id,
        )
        prompt = result.get("response", SLOT_COLLECT_INTROS.get(lang_key, SLOT_COLLECT_INTROS["en"]))
        return _build_response(prompt, session_attrs, "apply", session_attrs.get("language", "en"), requires_input=True)
    except Exception as e:
        logger.error(f"[ConnectWebhook] Apply handler error: {e}")
        return _build_response(
            PROCESSING_MESSAGES.get(lang_key, PROCESSING_MESSAGES["en"]),
            session_attrs, "apply", session_attrs.get("language", "en"), requires_input=False
        )


def _handle_grievance(session_id, transcript, lang_key, session_attrs, confidence):
    """Route grievance intent → workflow engine."""
    try:
        result = process_user_input(message=f"grievance:{transcript}", session_id=session_id)
        prompt = result.get("response", PROCESSING_MESSAGES.get(lang_key, PROCESSING_MESSAGES["en"]))
        return _build_response(prompt, session_attrs, "grievance", session_attrs.get("language", "en"), requires_input=False)
    except Exception as e:
        logger.error(f"[ConnectWebhook] Grievance handler error: {e}")
        return _build_response(PROCESSING_MESSAGES.get(lang_key, PROCESSING_MESSAGES["en"]), session_attrs, "grievance", "en", requires_input=False)


def _handle_track(session_id, lang_key, session_attrs):
    """Return tracking status from session."""
    try:
        result = process_user_input(message="track_status", session_id=session_id)
        prompt = result.get("response", "Your case is being processed.")
        return _build_response(prompt, session_attrs, "track", session_attrs.get("language", "en"), requires_input=False)
    except Exception as e:
        logger.error(f"[ConnectWebhook] Track handler error: {e}")
        return _build_response("Your application status is being checked. You will receive an SMS.", session_attrs, "track", "en", requires_input=False)


def _handle_info(session_id, transcript, lang_key, polly_svc, session_attrs):
    """RAG answer for info queries."""
    try:
        from app.services.rag_service import RAGService
        rag = RAGService()
        answer = rag.get_answer(transcript)
        if not answer:
            answer = "I will look into that for you. You will receive information via SMS."
        # Truncate to ≤400 chars for TTS (IVR prompt should be short)
        if len(answer) > 400:
            answer = answer[:397] + "..."
        return _build_response(answer, session_attrs, "info", session_attrs.get("language", "en"), requires_input=False)
    except Exception as e:
        logger.error(f"[ConnectWebhook] Info handler RAG error: {e}")
        return _build_response("I will send you information about that via SMS shortly.", session_attrs, "info", "en", requires_input=False)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _build_response(prompt: str, session_attrs: dict, intent: str, language: str, requires_input: bool) -> dict:
    return {
        "playPrompt": prompt,
        "sessionAttributes": session_attrs,
        "intent": intent,
        "language": language,
        "requiresInput": requires_input,
    }


def _detect_scheme(text: str) -> str:
    """Simple keyword-based scheme detection from transcript."""
    text_lower = text.lower()
    if any(k in text_lower for k in ["pm kisan", "kisan", "farmer", "किसान", "pm-kisan"]):
        return "pm_kisan"
    if any(k in text_lower for k in ["awas", "house", "housing", "home", "आवास"]):
        return "pm_awas_urban"
    if any(k in text_lower for k in ["shram", "e-shram", "labour", "श्रम"]):
        return "e_shram"
    return "pm_kisan"  # safe default
