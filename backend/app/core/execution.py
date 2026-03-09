"""
execution.py — JanSathi Execution Layer (AWS-Native)

OLD PATH (removed):  Flask → LangGraph → 9 local Python agents → AWS services
NEW PATH (this file): Flask → Bedrock AgentCore → Action Group Lambda → AWS services

This module is now a thin compatibility adapter.
All orchestration, tool-calling, and AI reasoning is done by Bedrock AgentCore.
The Bedrock Agent (BEDROCK_AGENT_ID) owns:
  - Intent classification  (classify_intent tool)
  - Knowledge retrieval    (retrieve_knowledge tool → Kendra)
  - Eligibility validation (validate_eligibility tool → DynamoDB rules)
  - Risk scoring           (compute_risk_score tool)
  - SMS dispatch           (send_sms_notification tool → SNS)
  - Receipt generation     (create_benefit_receipt tool → S3)
  - HITL escalation        (enqueue_hitl_case tool → SQS)
"""

import logging
import uuid

logger = logging.getLogger(__name__)


def process_user_input(
    message: str,
    session_id: str,
    language: str = "hi",
    user_profile: dict = None,
    channel: str = "web",
) -> dict:
    """
    Single entry point for all transport layers (Web, IVR, Lambda).

    Delegates entirely to Bedrock AgentCore. The Bedrock Agent orchestrates:
      classify_intent → retrieve_knowledge (Kendra) → validate_eligibility
      → compute_risk_score → create_benefit_receipt (S3) → send_sms_notification (SNS)
      → enqueue_hitl_case (SQS) if confidence is low

    Returns a dict with the same keys the calling routes expect so no routes
    need to change.
    """
    from agentcore.invoke import invoke_agentcore

    if not session_id or not isinstance(session_id, str):
        session_id = str(uuid.uuid4())

    result = invoke_agentcore(
        user_message=message or "",
        session_id=session_id,
        language=language or "hi",
        channel=channel or "web",
        slots=user_profile or {},
    )

    # Map AgentCore response keys → legacy shape expected by routes and callers
    return {
        "response":            result.get("response", ""),
        "response_text":       result.get("response", ""),   # alias kept for compat
        "session_id":          result.get("session_id", session_id),
        "thoughts":            result.get("thoughts", []),
        "citations":           result.get("citations", []),
        "benefit_receipt":     result.get("benefit_receipt"),
        "eligibility_score":   result.get("confidence", 0.9),
        "requires_input":      result.get("requires_input", False),
        "is_terminal":         result.get("is_terminal", False),
        # Life-event fields forwarded if AgentCore sets them
        "is_life_event":       result.get("is_life_event", False),
        "life_event_id":       result.get("life_event_id"),
        "life_event_label":    result.get("life_event_label"),
        "life_event_icon":     result.get("life_event_icon"),
        "life_event_summary":  result.get("life_event_summary"),
        "life_event_workflow": result.get("life_event_workflow", []),
        "mode":                "agentcore",
    }
