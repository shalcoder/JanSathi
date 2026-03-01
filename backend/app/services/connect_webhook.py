"""
connect_webhook.py – IVR / Amazon Connect Lambda entry point.

Handles incoming Connect invocations:
  1. Transcribes audio if S3 key provided (via TranscribeService)
  2. Classifies intent+language via IntentService
  3. Routes:
       apply     → workflow_engine slot collection
       info      → RAG + Polly TTS
       grievance → grievance handler
       track     → session status
  4. Returns {"playPrompt": "...", "sessionAttributes": {...}}
     for Amazon Connect to speak aloud.
"""

import logging
import os
from typing import Optional

from app.services.intent_service import IntentService
from app.services.polly_service import PollyService
from app.services.transcribe_service import TranscribeService
from app.core.execution import process_user_input

logger = logging.getLogger(__name__)

# Lazy singletons
_intent_service: Optional[IntentService] = None
_polly_service: Optional[PollyService] = None
_transcribe_service: Optional[TranscribeService] = None


def _get_services():
    global _intent_service, _polly_service, _transcribe_service
    if _intent_service is None:
        _intent_service = IntentService()
    if _polly_service is None:
        _polly_service = PollyService()
    if _transcribe_service is None:
        _transcribe_service = TranscribeService()
    return _intent_service, _polly_service, _transcribe_service


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
