"""
intent_agent.py — Agent 2: Intent Classification
=================================================
Responsibilities:
  - Classify user intent: apply | info | grievance | track | fallback
  - Detect scheme hint (pm_kisan, pm_awas_urban, e_shram, etc.)
  - Determine required slots for the intent+scheme combination

Strategy:
  1. Wrap existing RuleBasedIntentClassifier (fast, no cloud)
  2. If confidence < 0.75, escalate to Nova Micro via nova_converse_json
  3. Map intents to required_slots per scheme

Routing → rag_agent (always, to fetch scheme context)
"""
import logging
import sys
import os

from .state import JanSathiState
from .nova_client import nova_converse_json, build_user_message, NOVA_MICRO

logger = logging.getLogger(__name__)
SUPPORTED_LANGUAGES = {"hi", "en", "ta", "kn", "te", "mr", "bn", "gu", "pa", "or"}

# ── Slot schemas per intent+scheme ────────────────────────────────────────────
SCHEME_SLOTS = {
    "pm_kisan":       ["age", "land_area_acres", "state", "bank_account_linked", "aadhaar_linked"],
    "pm_awas_urban":  ["annual_income", "house_ownership", "state", "family_size"],
    "pm_awas_gramin": ["annual_income", "bpl_card", "state"],
    "e_shram":        ["age", "occupation", "aadhaar", "mobile"],
    "pmjay":          ["annual_income", "state", "family_size", "bpl_card"],
    "pmjdy":          ["mobile", "aadhaar", "state"],
    "mudra":          ["business_type", "loan_amount", "annual_income"],
    "unknown":        ["state", "occupation", "annual_income"],
}

INTENT_SLOTS = {
    "grievance": ["application_id", "issue_type"],
    "track":     ["application_id"],
    "info":      [],   # No mandatory slots for info intent
    "fallback":  [],
}

NOVA_INTENT_PROMPT = """You are an intent classifier for JanSathi, India's AI-powered civic assistance system.

Classify the user utterance and return ONLY a valid JSON object:
{{
  "intent": "<apply|info|grievance|track|fallback>",
  "confidence": <0.0-1.0>,
  "language_detected": "<hi|ta|kn|en|other>",
  "scheme_hint": "<pm_kisan|pm_awas_urban|pm_awas_gramin|e_shram|pmjay|pmjdy|mudra|unknown>",
  "required_slots": ["<slot1>", "<slot2>"]
}}

INTENT DEFINITIONS:
- apply: user wants to apply for/check eligibility for a government scheme
- info: user wants information about a scheme or documents required
- grievance: user has a complaint (payment not received, rejection, error)
- track: user wants status of existing application
- fallback: unclear or off-topic

USER UTTERANCE: {query}"""


def intent_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 2: Intent Classification Agent.
    Uses rule-based first, escalates to Nova Micro if confidence < 0.75.
    """
    session_id = state.get("session_id", "unknown")
    query = state.get("user_query", "")
    requested_language = state.get("language", "hi")

    logger.info(f"[IntentAgent] session={session_id} query='{query[:80]}'")

    # ── Step 1: Rule-based classification (fast, no cloud) ────────────────────
    try:
        # Import existing IntentService
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app.services.intent_service import RuleBasedIntentClassifier
        rule_clf = RuleBasedIntentClassifier()
        rule_result = rule_clf.classify(query, requested_language)
        intent = rule_result.get("intent", "fallback")
        confidence = float(rule_result.get("confidence", 0.0))
        scheme_hint = rule_result.get("scheme_hint", "unknown")
        lang_detected = rule_result.get("language_detected", requested_language)
    except Exception as e:
        logger.warning(f"[IntentAgent] Rule-based classifier failed: {e}")
        intent, confidence, scheme_hint, lang_detected = "fallback", 0.0, "unknown", requested_language

    # ── Step 2: If confidence < 0.75, escalate to Nova Micro ─────────────────
    if confidence < 0.75:
        logger.info(f"[IntentAgent] Low confidence ({confidence:.2f}), escalating to Nova Micro")
        prompt = NOVA_INTENT_PROMPT.format(query=query)
        nova_result = nova_converse_json(
            messages=[build_user_message(prompt)],
            model_id=NOVA_MICRO,
            max_tokens=256,
        )
        if nova_result:
            intent = nova_result.get("intent", intent)
            confidence = float(nova_result.get("confidence", confidence))
            scheme_hint = nova_result.get("scheme_hint", scheme_hint)
            lang_detected = nova_result.get("language_detected", lang_detected)

    # ── Step 3: Resolve required slots ───────────────────────────────────────
    if intent == "apply":
        required_slots = SCHEME_SLOTS.get(scheme_hint, SCHEME_SLOTS["unknown"])
    else:
        required_slots = INTENT_SLOTS.get(intent, [])

    logger.info(
        f"[IntentAgent] session={session_id} intent={intent} "
        f"confidence={confidence:.2f} scheme={scheme_hint} slots={required_slots}"
    )

    # Preserve caller-selected language for responses.
    # Keep detected language separately for analytics/debugging only.
    response_language = (
        requested_language
        if requested_language in SUPPORTED_LANGUAGES
        else (lang_detected if lang_detected in SUPPORTED_LANGUAGES else "en")
    )

    updated = dict(state)
    updated.update({
        "intent": intent,
        "intent_confidence": confidence,
        "scheme_hint": scheme_hint,
        "language": response_language,
        "language_detected": lang_detected,
        "required_slots": required_slots,
    })
    return updated
