"""
telecom_agent.py — Agent 1: Telecom Entry & Consent Gate
=========================================================
Responsibilities:
  - Validate channel (ivr | web | sms)
  - Capture user consent (DPDP compliance)
  - Detect language (from IVR DTMF or web header)
  - Route to END if consent is not given

Routing:
  consent_given=True  → intent_agent
  consent_given=False → END (no further processing)
"""
import logging
from .state import JanSathiState

logger = logging.getLogger(__name__)

SUPPORTED_CHANNELS = {"ivr", "web", "sms"}
SUPPORTED_LANGUAGES = {"hi", "en", "ta", "kn", "te", "mr", "bn", "gu", "pa", "or"}


def telecom_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 1: Telecom/Entry Agent.
    Handles consent capture and channel/language validation.
    """
    session_id = state.get("session_id", "unknown")
    channel = state.get("channel", "web")
    language = state.get("language", "hi")

    logger.info(f"[TelecomAgent] session={session_id} channel={channel} lang={language}")

    # ── Validate channel ──────────────────────────────────────────────────────
    if channel not in SUPPORTED_CHANNELS:
        logger.warning(f"[TelecomAgent] Unknown channel '{channel}', defaulting to 'web'")
        channel = "web"

    # ── Validate language ──────────────────────────────────────────────────────
    if language not in SUPPORTED_LANGUAGES:
        logger.warning(f"[TelecomAgent] Unknown language '{language}', defaulting to 'hi'")
        language = "hi"

    # ── Consent capture ────────────────────────────────────────────────────────
    # For web channel: consent is assumed from frontend checkbox (passed in state)
    # For IVR: consent captured via DTMF "1" (press 1 to accept)
    consent = state.get("consent_given", False)

    if not consent:
        # Web: default to True if no explicit denial (frontend sends consent_given=true)
        # IVR: if no consent in state, default web to True, IVR to False (pending DTMF)
        if channel == "web":
            consent = True  # Frontend checkbox collected consent
        else:
            consent = False  # IVR must explicitly press 1
            logger.warning(f"[TelecomAgent] session={session_id} — Consent not given on IVR channel")

    updated = dict(state)
    updated.update({
        "channel": channel,
        "language": language,
        "consent_given": consent,
        "error": "" if consent else "CONSENT_DENIED",
    })

    if consent:
        logger.info(f"[TelecomAgent] session={session_id} — Consent granted. Proceeding to intent.")
    else:
        logger.warning(f"[TelecomAgent] session={session_id} — Consent denied. Stopping pipeline.")

    return updated


def should_continue_after_telecom(state: JanSathiState) -> str:
    """
    Conditional edge after telecom_agent.
    Returns:
      "intent_agent"  — if consent given
      "__end__"       — if consent denied
    """
    if state.get("error") == "CONSENT_DENIED" or not state.get("consent_given", False):
        return "__end__"
    return "intent_agent"
