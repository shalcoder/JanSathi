"""
agentcore/tools.py — JanSathi Tool Definitions for Bedrock AgentCore
====================================================================
Each function here becomes an "Action Group" in the Bedrock Agent.
AgentCore will call these tools when orchestrating the agent pipeline.

Tool design: each tool represents one major LangGraph agent node,
with clear input/output schemas that AgentCore can parse and route.
"""
import json
import logging
import sys
import os

logger = logging.getLogger(__name__)

# Ensure backend/ is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Tool 1: Classify Intent ────────────────────────────────────────────────────

def classify_intent(query: str, language: str = "hi", session_id: str = "") -> dict:
    """
    Classify the user's intent from their query.
    Returns intent, confidence, scheme_hint, and required_slots.
    """
    try:
        from app.services.intent_service import IntentService
        svc = IntentService()
        result = svc.classify_intent_ivr(query, language)
        return {
            "success": True,
            "intent": result.get("intent", "info"),
            "confidence": result.get("confidence", 0.75),
            "scheme_hint": result.get("scheme_hint", "unknown"),
            "language_detected": result.get("language_detected", language),
            "required_slots": result.get("required_slots", []),
        }
    except Exception as e:
        logger.error(f"[Tool:classify_intent] Error: {e}")
        return {"success": False, "error": str(e), "intent": "fallback"}


# ── Tool 2: Retrieve Knowledge ────────────────────────────────────────────────

def retrieve_knowledge(query: str, scheme_hint: str = "unknown", language: str = "hi") -> dict:
    """
    Retrieve relevant scheme information from the knowledge base.
    Returns a list of context chunks about the scheme.
    """
    try:
        from app.services.rag_service import RagService
        rag = RagService()
        enriched_query = f"{scheme_hint.replace('_', ' ')} {query}"
        results = rag.retrieve(enriched_query, language=language)
        return {
            "success": True,
            "context_chunks": results[:4],
            "source_count": len(results),
        }
    except Exception as e:
        logger.error(f"[Tool:retrieve_knowledge] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "context_chunks": ["Please visit india.gov.in for scheme information."],
        }


# ── Tool 3: Validate Eligibility ──────────────────────────────────────────────

def validate_eligibility(slots: dict, scheme_hint: str = "unknown") -> dict:
    """
    Deterministically validate user eligibility for a scheme.
    Uses the RulesEngine — NO LLM involved.
    Returns eligible (bool), score (0-1), and breakdown.
    """
    # Import embedded rules from rules_agent
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from agents.rules_agent import SCHEME_RULES
        from app.services.rules_engine import RulesEngine

        rules = SCHEME_RULES.get(scheme_hint, SCHEME_RULES.get("unknown", {"mandatory": []}))
        engine = RulesEngine()
        eligible, breakdown, score = engine.evaluate(user_profile=slots, rules=rules)
        return {
            "success": True,
            "eligible": eligible,
            "score": float(score),
            "breakdown": breakdown,
        }
    except Exception as e:
        logger.error(f"[Tool:validate_eligibility] Error: {e}")
        return {"success": False, "error": str(e), "eligible": False, "score": 0.0}


# ── Tool 4: Compute Risk & Route ─────────────────────────────────────────────

def compute_risk_score(
    session_id: str,
    rules_score: float,
    eligible: bool,
    intent_confidence: float = 0.85,
    asr_confidence: float = 1.0,
) -> dict:
    """
    Compute composite risk score and determine routing decision.
    Returns: risk_score, decision (AUTO_SUBMIT|HITL_QUEUE|NOT_ELIGIBLE_NOTIFY), reasons.
    """
    try:
        from app.services.verifier_service import VerifierService
        verifier = VerifierService()
        result = verifier.assess(
            session_id=session_id,
            rules_score=rules_score,
            eligible=eligible,
            asr_confidence=asr_confidence,
            intent_confidence=intent_confidence,
        )
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"[Tool:compute_risk_score] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "decision": "NOT_ELIGIBLE_NOTIFY",
            "risk_score": 0.0,
        }


# ── Tool 5: Generate Response ─────────────────────────────────────────────────

def generate_response(
    query: str,
    context_chunks: list,
    language: str = "hi",
    intent: str = "info",
    scheme_hint: str = "unknown",
    eligibility_status: str = "unknown",
) -> dict:
    """
    Generate the final AI response using Amazon Nova Lite.
    Returns the response text and a Benefit Receipt if eligible.
    """
    try:
        from app.services.bedrock_service import BedrockService
        context_text = "\n\n".join(context_chunks[:3]) if context_chunks else ""
        bedrock = BedrockService()
        result = bedrock.generate_response(query, context_text, language, intent)
        return {
            "success": True,
            "response_text": result.get("text", ""),
            "provenance": result.get("provenance", "unknown"),
        }
    except Exception as e:
        logger.error(f"[Tool:generate_response] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response_text": "कृपया india.gov.in पर जाएं / Please visit india.gov.in",
        }


# ── Tool 6: Send SMS Notification ─────────────────────────────────────────────

def send_sms_notification(
    phone: str, scheme: str, case_id: str, notification_type: str = "submission"
) -> dict:
    """
    Send SMS notification to the citizen via AWS SNS.
    notification_type: 'submission' | 'hitl_queued' | 'rejected'
    """
    try:
        from app.services.notify_service import NotifyService
        notify = NotifyService()
        if notification_type == "submission":
            result = notify.notify_submission(phone, scheme, case_id)
        elif notification_type == "hitl_queued":
            result = notify.notify_hitl_queued(phone, scheme, case_id)
        else:
            result = notify.notify_rejected(phone, scheme, case_id)
        return {"success": result.get("success", False), "message_id": result.get("message_id", "")}
    except Exception as e:
        logger.error(f"[Tool:send_sms_notification] Error: {e}")
        return {"success": False, "error": str(e)}


# ── Tool 7: Enqueue HITL Case ────────────────────────────────────────────────

def enqueue_hitl_case(
    session_id: str,
    transcript: str,
    response_text: str,
    confidence: float,
    slots: dict = None,
) -> dict:
    """
    Escalate a case to the Human-in-the-Loop review queue.
    Returns the HITL case ID.
    """
    try:
        from app.services.hitl_service import HITLService
        hitl = HITLService()
        case = hitl.enqueue_case(
            session_id=session_id,
            turn_id=f"turn-{session_id}",
            transcript=transcript,
            response_text=response_text,
            confidence=confidence,
            slots=slots or {},
        )
        return {"success": True, "case_id": case.get("id", ""), "status": case.get("status", "")}
    except Exception as e:
        logger.error(f"[Tool:enqueue_hitl_case] Error: {e}")
        return {"success": False, "error": str(e), "case_id": ""}


# ── Tool registry (for AgentCore Action Group schema generation) ──────────────

TOOL_REGISTRY = {
    "classify_intent": classify_intent,
    "retrieve_knowledge": retrieve_knowledge,
    "validate_eligibility": validate_eligibility,
    "compute_risk_score": compute_risk_score,
    "generate_response": generate_response,
    "send_sms_notification": send_sms_notification,
    "enqueue_hitl_case": enqueue_hitl_case,
}


def dispatch_tool(tool_name: str, parameters: dict) -> dict:
    """Dispatch a tool call by name. Used by the AgentCore invoke handler."""
    if tool_name not in TOOL_REGISTRY:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    try:
        return TOOL_REGISTRY[tool_name](**parameters)
    except TypeError as e:
        return {"success": False, "error": f"Invalid parameters for {tool_name}: {e}"}
