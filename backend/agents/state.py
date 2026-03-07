"""
state.py — Shared JanSathi LangGraph Agent State
=================================================
Single TypedDict that flows through all 9 agent nodes.
Every agent reads from and writes to this shared object.
"""
from typing import TypedDict, Optional, List, Dict, Any


class JanSathiState(TypedDict, total=False):
    # ── Session Identity ──────────────────────────────────────────────────────
    session_id: str                  # Unique session identifier
    channel: str                     # "ivr" | "web" | "sms"
    language: str                    # "hi" | "en" | "ta" | "kn" | ...
    user_query: str                  # Current user message/utterance

    # ── Consent & Privacy ─────────────────────────────────────────────────────
    consent_given: bool              # MUST be True to proceed (DPDP compliance)

    # ── Intent Classification ─────────────────────────────────────────────────
    intent: str                      # "apply" | "info" | "grievance" | "track" | "fallback"
    intent_confidence: float         # 0.0 – 1.0 from intent_agent
    scheme_hint: str                 # "pm_kisan" | "pm_awas_urban" | "e_shram" | "unknown"
    required_slots: List[str]        # Slot names needed for this intent+scheme

    # ── Slot Collection ───────────────────────────────────────────────────────
    slots: Dict[str, Any]            # Collected user profile fields (age, income, etc.)
    slots_complete: bool             # True when all required_slots are filled

    # ── RAG Context ───────────────────────────────────────────────────────────
    rag_context: List[str]           # Retrieved scheme knowledge chunks

    # ── Eligibility & Verification ────────────────────────────────────────────
    eligibility_result: Dict[str, Any]   # {eligible, breakdown, score} from RulesEngine
    verifier_result: Dict[str, Any]      # {risk_score, decision, reasons} from VerifierService

    # ── Response Generation ───────────────────────────────────────────────────
    response_text: str               # Final AI-generated response to user
    benefit_receipt: Dict[str, Any]  # Generated Benefit Receipt

    # ── HITL ──────────────────────────────────────────────────────────────────
    hitl_case_id: str                # Set if escalated to HITL queue

    # ── Notifications ─────────────────────────────────────────────────────────
    phone: str                       # User phone number for SMS
    sms_sent: bool                   # True after SMS dispatched

    # ── IVR / Audio Signals ───────────────────────────────────────────────────
    asr_confidence: float            # 1.0 for web/text; 0–1 for IVR audio input

    # ── LangGraph Message History ─────────────────────────────────────────────
    messages: List[Dict[str, Any]]   # Nova Converse API message history

    # ── Error Handling ────────────────────────────────────────────────────────
    error: str                       # Fatal error message (routes to END)


# ── Default state factory ──────────────────────────────────────────────────────

def initial_state(
    session_id: str,
    channel: str = "web",
    language: str = "hi",
    user_query: str = "",
    phone: str = "",
    asr_confidence: float = 1.0,
) -> JanSathiState:
    """Create a fresh JanSathiState with safe defaults."""
    return JanSathiState(
        session_id=session_id,
        channel=channel,
        language=language,
        user_query=user_query,
        consent_given=False,
        intent="fallback",
        intent_confidence=0.0,
        scheme_hint="unknown",
        required_slots=[],
        slots={},
        slots_complete=False,
        rag_context=[],
        eligibility_result={},
        verifier_result={},
        response_text="",
        benefit_receipt={},
        hitl_case_id="",
        phone=phone,
        sms_sent=False,
        asr_confidence=asr_confidence,
        messages=[],
        error="",
    )
