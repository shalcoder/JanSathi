"""
hitl_agent.py — Agent 9: Human-in-the-Loop Escalation
======================================================
Responsibilities:
  - Enqueue low-confidence/HITL_QUEUE cases to HITLService
  - Use Nova Pro to write a rich case summary for the human reviewer
  - Set state["hitl_case_id"]
  - Then routes to notification_agent

Triggered when: verifier_result["decision"] == "HITL_QUEUE"
"""
import os
import sys
import logging

from .state import JanSathiState
from .nova_client import nova_converse, build_user_message, NOVA_PRO

logger = logging.getLogger(__name__)

CASE_SUMMARY_PROMPT = """You are a case analyst for JanSathi, India's civic AI system.

Write a concise case summary for a human reviewer to assess this citizen's eligibility application.

SESSION: {session_id}
SCHEME: {scheme}
INTENT: {intent}
USER QUERY: {query}
LANGUAGE: {language}

COLLECTED DATA (citizen's profile):
{slots}

ELIGIBILITY CHECK RESULTS:
{eligibility_breakdown}

RISK SIGNALS:
{risk_reasons}

Write a 3-5 sentence professional case summary that:
1. States who the citizen is (based on collected slots)
2. Which scheme they're applying for and why they were flagged for review
3. Which eligibility conditions passed and which failed
4. What the human reviewer should focus on
5. Recommend approve/reject based on data

Keep factual and objective. Do NOT invent information."""


def hitl_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 9: HITL Escalation Agent.
    Enqueues case to HITLService and generates case summary.
    """
    session_id = state.get("session_id", "unknown")
    scheme_hint = state.get("scheme_hint", "unknown")
    query = state.get("user_query", "")
    language = state.get("language", "hi")
    intent = state.get("intent", "apply")
    slots = state.get("slots", {})
    eligibility_result = state.get("eligibility_result", {})
    verifier_result = state.get("verifier_result", {})
    response_text = state.get("response_text", "")

    logger.info(f"[HITLAgent] session={session_id} scheme={scheme_hint}")

    # ── Format eligibility breakdown for case summary ─────────────────────────
    breakdown = eligibility_result.get("breakdown", [])
    breakdown_text = "\n".join(
        f"{'PASS' if r.get('pass') else 'FAIL'}: {r.get('label', '')} "
        f"(Value: {r.get('user_value', 'N/A')}, Required: {r.get('required_value', 'N/A')})"
        for r in breakdown if isinstance(r, dict)
    ) or "No breakdown available"

    risk_reasons = "\n".join(verifier_result.get("reasons", ["No specific reasons"]))
    confidence = verifier_result.get("risk_score", 0.7)

    # ── Generate AI case summary using Nova Pro ───────────────────────────────
    prompt = CASE_SUMMARY_PROMPT.format(
        session_id=session_id,
        scheme=scheme_hint.replace("_", " ").title(),
        intent=intent,
        query=query,
        language=language,
        slots=_format_slots(slots),
        eligibility_breakdown=breakdown_text,
        risk_reasons=risk_reasons,
    )

    case_summary = nova_converse(
        messages=[build_user_message(prompt)],
        model_id=NOVA_PRO,
        system_prompt=(
            "You are a professional government case analyst. "
            "Write objective, factual case summaries for human reviewers. "
            "Be concise, structured, and neutral."
        ),
        max_tokens=400,
        temperature=0.1,
    )

    # ── Enqueue to HITLService ────────────────────────────────────────────────
    hitl_case_id = ""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app.services.hitl_service import HITLService
        hitl = HITLService()
        case = hitl.enqueue_case(
            session_id=session_id,
            turn_id=f"turn-{session_id}",
            transcript=query,
            response_text=response_text or case_summary,
            confidence=float(confidence),
            benefit_receipt=state.get("benefit_receipt", {}),
            slots=slots,
        )
        hitl_case_id = case.get("id", "")
        logger.info(f"[HITLAgent] Case enqueued: {hitl_case_id}")
    except Exception as e:
        logger.error(f"[HITLAgent] HITLService enqueue failed: {e}")
        hitl_case_id = f"local-hitl-{session_id}"

    # ── Generate citizen-facing HITL response ────────────────────────────────
    lang_messages = {
        "hi": (
            f"✅ आपका आवेदन हमें प्राप्त हो गया है।\n\n"
            f"📋 **केस ID**: {hitl_case_id}\n\n"
            f"आपका मामला एक विशेषज्ञ द्वारा 24 घंटों के भीतर समीक्षा किया जाएगा। "
            f"हम आपको SMS के माध्यम से सूचित करेंगे।\n\n"
            f"🌐 **आधिकारिक पोर्टल**: [myscheme.gov.in](https://myscheme.gov.in)"
        ),
        "en": (
            f"✅ Your application has been received.\n\n"
            f"📋 **Case ID**: {hitl_case_id}\n\n"
            f"Your case will be reviewed by a human expert within 24 hours. "
            f"We will notify you via SMS.\n\n"
            f"🌐 **Official Portal**: [myscheme.gov.in](https://myscheme.gov.in)"
        ),
    }
    citizen_response = lang_messages.get(language, lang_messages["en"])

    updated = dict(state)
    updated["hitl_case_id"] = hitl_case_id
    updated["response_text"] = citizen_response
    return updated


def _format_slots(slots: dict) -> str:
    """Format slots dict for readable case summary."""
    if not slots:
        return "No profile data collected"
    return "\n".join(f"  {k}: {v}" for k, v in slots.items())
