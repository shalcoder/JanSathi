"""
response_agent.py — Agent 7: Response Synthesis
================================================
Responsibilities:
  - Synthesize RAG context + eligibility result into a human-readable response
  - Use Nova Lite with JanSathi's structured prompt template
  - Generate a Benefit Receipt for eligible users
  - Validate response for hallucinations (known domains check)
"""
import re
import uuid
import logging
import json
from datetime import datetime, timezone

from .state import JanSathiState
from .nova_client import nova_converse, build_user_message, NOVA_LITE

logger = logging.getLogger(__name__)

KNOWN_DOMAINS = [
    "gov.in", "nic.in", "india.gov.in", "pmkisan.gov.in",
    "pmjay.gov.in", "enam.gov.in", "pmfby.gov.in", "pmaymis.gov.in",
    "pmuy.gov.in", "mudra.org.in", "nsiindia.gov.in", "pmjdy.gov.in",
    "nfsa.gov.in", "pmvishwakarma.gov.in", "pmsvanidhi.mohua.gov.in",
    "pmkvyofficial.org", "edistrict.up.gov.in", "myscheme.gov.in",
    "eshram.gov.in", "umang.gov.in", "digilocker.gov.in",
]

RESPONSE_PROMPT = """You are JanSathi, India's premier AI Citizen Assistant.

VERIFIED SCHEME INFORMATION:
{rag_context}

USER QUERY: {query}
LANGUAGE: {language}
INTENT: {intent}
SCHEME: {scheme}

ELIGIBILITY STATUS: {eligibility_status}
DECISION: {decision}

INSTRUCTIONS:
1. Respond ONLY in {language}
2. Use the verified scheme information above — do NOT invent data
3. Every amount/date/eligibility criterion must come from the context
4. If context is insufficient, direct to myscheme.gov.in
5. Be empathetic, clear, and use simple language
6. Structure your response clearly

RESPONSE FORMAT (use Markdown):
✅ **Summary**: [1-2 sentence overview]

📋 **Key Details**:
• [Important points from context]

🪜 **Your Action Plan**:
1. [Step 1]
2. [Step 2]

🛡️ **Eligibility Status**: {eligibility_status}

🌐 **Official Source**: [Official government URL from context]"""


def response_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 7: Response Synthesis Agent.
    Generates final response using Nova Lite + RAG context.
    Creates a Benefit Receipt for eligible auto-submit cases.
    Handles life_event intent by building a structured cascade response.
    """
    session_id = state.get("session_id", "unknown")
    query = state.get("user_query", "")
    language = state.get("language", "hi")
    intent = state.get("intent", "info")

    # ── Life event fast path ─────────────────────────────────────────────────
    if intent == "life_event" and state.get("is_life_event"):
        return _handle_life_event_response(state)

    rag_context = state.get("rag_context", [])
    eligibility_result = state.get("eligibility_result", {})
    verifier_result = state.get("verifier_result", {})
    scheme_hint = state.get("scheme_hint", "unknown")
    scheme_hint = state.get("scheme_hint", "unknown")

    logger.info(f"[ResponseAgent] session={session_id} intent={intent} scheme={scheme_hint}")

    decision = verifier_result.get("decision", "AUTO_SUBMIT")
    verifier_explanation = verifier_result.get("explanation", "")
    eligible = eligibility_result.get("eligible", True)

    # Format eligibility status
    if eligible:
        eligibility_status = "✅ Eligible"
    else:
        eligibility_status = "⚠️ Not Eligible (see details below)"

    # Format RAG context
    context_text = "\n\n".join(rag_context[:3]) if rag_context else "General government scheme information."

    # Build Nova Lite prompt
    prompt = RESPONSE_PROMPT.format(
        rag_context=context_text,
        query=query,
        language=language,
        intent=intent,
        scheme=scheme_hint.replace("_", " ").title(),
        eligibility_status=eligibility_status,
        decision=decision,
    )

    # Call Nova Lite
    response_text = nova_converse(
        messages=[build_user_message(prompt)],
        model_id=NOVA_LITE,
        system_prompt=_get_jansathi_system_prompt(),
        max_tokens=1200,
        temperature=0.1,
    )

    # Append verifier explanation if available
    if verifier_explanation and verifier_explanation not in response_text:
        response_text += f"\n\n---\n💡 **Assessment**: {verifier_explanation}"

    # Validate response (hallucination check)
    response_text = _validate_response(response_text)

    # Generate Benefit Receipt for eligible cases
    benefit_receipt = {}
    if eligible and decision == "AUTO_SUBMIT":
        benefit_receipt = _generate_benefit_receipt(state, response_text)

    logger.info(f"[ResponseAgent] session={session_id} response_len={len(response_text)} receipt={bool(benefit_receipt)}")

    updated = dict(state)
    updated["response_text"] = response_text
    updated["benefit_receipt"] = benefit_receipt
    return updated


def _validate_response(response: str) -> str:
    """Validate and sanitize AI response — remove fabricated URLs."""
    if not response:
        return "I could not generate a response. Please visit india.gov.in for assistance."

    # Remove Human:/Assistant: markers
    response = re.sub(r"^(Human|Assistant):\s*", "", response, flags=re.MULTILINE)

    # Replace unrecognized URLs with safe fallback
    urls = re.findall(r"https?://[^\s\)\]]+", response)
    for url in urls:
        if not any(domain in url for domain in KNOWN_DOMAINS):
            response = response.replace(url, "https://myscheme.gov.in")

    return response.strip()


def _handle_life_event_response(state: JanSathiState) -> JanSathiState:
    """
    Build a structured response for a detected life event.
    Returns a short human-readable summary + structured workflow in state.
    No LLM call needed — response is template-based + structured data.
    """
    session_id    = state.get("session_id", "unknown")
    event_label   = state.get("life_event_label", "Life Event")
    icon          = state.get("life_event_icon", "🏛️")
    workflow      = state.get("life_event_workflow", [])
    summary       = state.get("life_event_summary", "I've found government services that can help.")
    language      = state.get("language", "hi")

    # Urgent steps (priority == "urgent")
    urgent = [s for s in workflow if s.get("priority") == "urgent"]
    urgent_labels = [f"**{s['label']}**" for s in urgent]

    # Build readable markdown response
    lines = [
        f"{icon} **{event_label} — Government Services Triggered**\n",
        summary,
        "",
    ]
    for i, step in enumerate(workflow, 1):
        priority_badge = {"urgent": "🔴 URGENT", "high": "🟠 HIGH", "medium": "🟡 MEDIUM", "low": "🟢 LOW"}.get(step.get("priority", "medium"), "")
        lines.append(f"**Step {i}: {step['label']}** {priority_badge}")
        lines.append(f"{step['description']}")
        lines.append(f"→ {step['action']}")
        if step.get("link"):
            lines.append(f"🔗 [Apply / More Info]({step['link']})")
        lines.append("")

    lines.append("---")
    lines.append("💬 Ask me about any of these steps for detailed guidance. I can help you check eligibility, prepare documents, or fill applications.")

    response_text = "\n".join(lines)

    logger.info(f"[ResponseAgent/LifeEvent] session={session_id} event={state.get('life_event_id')} steps={len(workflow)}")

    updated = dict(state)
    updated["response_text"] = response_text
    updated["benefit_receipt"] = {}
    return updated


def _generate_benefit_receipt(state: JanSathiState, response_text: str) -> dict:
    """Generate a structured Benefit Receipt for eligible auto-submit cases."""
    now = datetime.now(timezone.utc).isoformat()
    receipt_id = f"BR-{uuid.uuid4().hex[:10].upper()}"
    eligibility_result = state.get("eligibility_result", {})

    return {
        "receipt_id": receipt_id,
        "session_id": state.get("session_id"),
        "scheme": state.get("scheme_hint", "unknown").replace("_", " ").upper(),
        "timestamp": now,
        "eligibility_score": eligibility_result.get("score", 0),
        "breakdown": eligibility_result.get("breakdown", []),
        "risk_score": state.get("verifier_result", {}).get("risk_score", 0),
        "decision": "AUTO_SUBMIT",
        "language": state.get("language", "hi"),
        "slots": state.get("slots", {}),
        "response_summary": response_text[:500],
        "generated_by": "JanSathi AI — amazon.nova-lite-v1:0",
        "privacy_notice": "Data processed with DPDP-compliant consent. Zero PII in logs.",
    }


def _get_jansathi_system_prompt() -> str:
    """JanSathi system instruction for Nova."""
    return (
        "You are JanSathi, India's premier AI Citizen Assistant. "
        "Your mission is to provide accurate, compassionate, and actionable guidance "
        "about Indian government schemes to rural citizens. "
        "Always use verified information from the context provided. "
        "Never invent eligibility data, amounts, or deadlines. "
        "Use simple, clear language that uneducated rural citizens can understand. "
        "Be warm, supportive, and empathetic in your tone."
    )
