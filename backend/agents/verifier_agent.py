"""
verifier_agent.py — Agent 6: Risk Assessment & Decision Routing
===============================================================
Responsibilities:
  - Composite risk scoring (ASR confidence + rules score + intent confidence + caller history)
  - Route to: AUTO_SUBMIT | HITL_QUEUE | NOT_ELIGIBLE_NOTIFY
  - Use Nova Pro to generate a human-readable decision explanation

Decision thresholds (from verifier_service.py):
  risk_score >= 0.85  → AUTO_SUBMIT  → response_agent → notification_agent
  0.60 <= score < 0.85 → HITL_QUEUE  → hitl_agent → notification_agent
  score < 0.60        → NOT_ELIGIBLE → notification_agent
"""
import os
import sys
import logging
from typing import List

from .state import JanSathiState
from .nova_client import nova_converse, build_user_message, NOVA_PRO

logger = logging.getLogger(__name__)


def verifier_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 6: Verifier Agent.
    Computes composite risk score and routes the session.
    """
    session_id = state.get("session_id", "unknown")
    eligibility_result = state.get("eligibility_result", {})
    intent_confidence = float(state.get("intent_confidence", 0.85))
    asr_confidence = float(state.get("asr_confidence", 1.0))
    intent = state.get("intent", "info")

    eligible = eligibility_result.get("eligible", True)
    rules_score = float(eligibility_result.get("score", 0.75))

    logger.info(
        f"[VerifierAgent] session={session_id} eligible={eligible} "
        f"rules_score={rules_score:.2f} intent_conf={intent_confidence:.2f}"
    )

    # ── For info/track/grievance, skip risk scoring ───────────────────────────
    if intent in ("info", "track", "grievance", "fallback"):
        updated = dict(state)
        updated["verifier_result"] = {
            "risk_score": 0.90,
            "decision": "AUTO_SUBMIT",
            "reasons": [f"Intent '{intent}' does not require eligibility scoring"],
            "signals": {},
        }
        return updated

    # ── Run VerifierService ───────────────────────────────────────────────────
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app.services.verifier_service import VerifierService
        verifier = VerifierService()
        caller_clean = verifier.get_caller_history_flag(session_id)
        verifier_result = verifier.assess(
            session_id=session_id,
            rules_score=rules_score,
            eligible=eligible,
            asr_confidence=asr_confidence,
            intent_confidence=intent_confidence,
            caller_history_clean=caller_clean,
        )
    except Exception as e:
        logger.error(f"[VerifierAgent] VerifierService failed: {e}")
        risk_score = rules_score * 0.5 + intent_confidence * 0.5
        decision = (
            "AUTO_SUBMIT" if risk_score >= 0.85
            else "HITL_QUEUE" if risk_score >= 0.60
            else "NOT_ELIGIBLE_NOTIFY"
        )
        verifier_result = {
            "risk_score": round(risk_score, 4),
            "decision": decision,
            "reasons": [f"Fallback scoring (VerifierService unavailable): {e}"],
            "signals": {},
        }

    # ── Generate human-readable explanation with Nova Pro ────────────────────
    decision = verifier_result.get("decision", "HITL_QUEUE")
    reasons = verifier_result.get("reasons", [])
    explanation = _generate_decision_explanation(
        decision=decision,
        reasons=reasons,
        eligibility_result=eligibility_result,
        language=state.get("language", "hi"),
    )
    verifier_result["explanation"] = explanation

    logger.info(
        f"[VerifierAgent] session={session_id} "
        f"risk={verifier_result['risk_score']:.3f} decision={decision}"
    )

    updated = dict(state)
    updated["verifier_result"] = verifier_result
    return updated


def should_route_after_verifier(state: JanSathiState) -> str:
    """
    Conditional edge after verifier_agent.
    Routes to response_agent (AUTO_SUBMIT/NOT_ELIGIBLE) or hitl_agent (HITL_QUEUE).
    """
    decision = state.get("verifier_result", {}).get("decision", "NOT_ELIGIBLE_NOTIFY")
    if decision == "HITL_QUEUE":
        return "hitl_agent"
    return "response_agent"


def _generate_decision_explanation(
    decision: str, reasons: List[str], eligibility_result: dict, language: str
) -> str:
    """Use Nova Pro to generate a compassionate, simple explanation of the decision."""
    breakdown = eligibility_result.get("breakdown", [])
    breakdown_text = "\n".join(
        f"{'✅' if r.get('pass') else '❌'} {r.get('label', '')} "
        f"(Your value: {r.get('user_value', 'N/A')})"
        for r in breakdown if isinstance(r, dict)
    )

    decision_labels = {
        "AUTO_SUBMIT": "Eligible — Ready for submission",
        "HITL_QUEUE": "Under review — Human expert will verify",
        "NOT_ELIGIBLE_NOTIFY": "Currently not eligible",
    }

    prompt = f"""You are JanSathi, a compassionate AI assistant for Indian citizens.

Explain this government scheme eligibility decision in simple, empathetic {language}.

DECISION: {decision_labels.get(decision, decision)}
ELIGIBILITY CHECK RESULTS:
{breakdown_text}

ADDITIONAL REASONS: {', '.join(reasons)}

Instructions:
1. Use simple, clear language (not bureaucratic)
2. If NOT_ELIGIBLE: be compassionate, explain which condition failed, suggest alternatives
3. If HITL_QUEUE: reassure the citizen their case is being reviewed personally
4. If AUTO_SUBMIT: congratulate and explain next steps
5. Keep to 3-4 sentences maximum
6. Respond in {language}"""

    try:
        return nova_converse(
            messages=[build_user_message(prompt)],
            model_id=NOVA_PRO,
            max_tokens=300,
            temperature=0.2,
        )
    except Exception:
        return f"Decision: {decision}. {' '.join(reasons[:2])}"
