"""
agent_service.py — Compatibility shim for legacy routes.

AgentService has been superseded by JanSathiSupervisor.
See: app/agent/supervisor.py

Legacy code that calls AgentService.orchestrate_query() is now
forwarded to JanSathiSupervisor.orchestrate() so the full 9-agent
pipeline runs consistently for ALL entry points.

DO NOT add new logic here.
"""

import logging
logger = logging.getLogger(__name__)


class AgentService:
    """
    Backward-compat shim. All calls delegate to JanSathiSupervisor.
    Accepts the same constructor signature as the old class to avoid
    breaking routes.py or any other caller that instantiates it with
    bedrock_service, rag_service, polly_service.
    """

    def __init__(self, bedrock_service=None, rag_service=None,
                 polly_service=None, rules_engine=None):
        # Keep references in case they are accessed externally
        self.bedrock_service = bedrock_service
        self.rag_service     = rag_service
        self.polly_service   = polly_service
        logger.info("[AgentService] Shim initialised — delegates to JanSathiSupervisor.")

    def orchestrate_query(self, user_query: str, language: str = "en",
                          user_id: str = None) -> dict:
        """
        Forward to JanSathiSupervisor and return a response shape
        compatible with the old schema so legacy routes don't break.
        """
        from app.agent.supervisor import get_supervisor
        result = get_supervisor().orchestrate({
            "session_id": user_id or "legacy",
            "message":    user_query,
            "language":   language,
            "channel":    "web",
            "consent":    True,
        })
        # Map new shape → old shape
        return {
            "text":               result.get("response_text", ""),
            "structured_sources": result.get("benefit_receipt", {}).get("sources", []),
            "context":            [],
            "explainability": {
                "confidence":                result.get("verifier", {}).get("risk_score", 0.85),
                "matching_criteria":         result.get("verifier", {}).get("reasons", []),
                "deterministic_verification": [],
            },
            "provenance":     "supervisor_pipeline",
            "execution_log":  [result.get("debug", {})],
        }
