"""
life_event_agent.py — Agent 0b: Life Event Detection
=====================================================
Intercepts queries that describe real-life citizen events (crop failure,
child birth, job loss, etc.) and expands them into cascaded multi-service
workflow objects — before the rest of the pipeline runs.

If a life event is detected:
  - Populates state with the full workflow steps
  - Routes DIRECTLY to response_agent (skips slots/rules/verifier)

If not a life event:
  - Passes through to intent_agent unchanged

This runs immediately after telecom_agent (consent gate).
"""
import logging
from .state import JanSathiState
from .life_events import detect_life_event

logger = logging.getLogger(__name__)


def life_event_agent(state: JanSathiState) -> JanSathiState:
    """
    Detect life events in the user query and populate workflow state.
    Runs before intent_agent — zero latency (pure local keyword matching).
    """
    query    = state.get("user_query", "")
    language = state.get("language", "hi")
    session  = state.get("session_id", "unknown")

    detected = detect_life_event(query, language)

    if detected:
        logger.info(
            f"[LifeEventAgent] session={session} "
            f"event='{detected['event_id']}' steps={detected['step_count']}"
        )
        return {
            **state,
            "is_life_event":        True,
            "life_event_id":        detected["event_id"],
            "life_event_label":     detected["event_label"],
            "life_event_icon":      detected["icon"],
            "life_event_workflow":  detected["steps"],
            "life_event_summary":   detected["summary"],
            # Set intent so response_agent formats correctly
            "intent":               "life_event",
        }

    logger.debug(f"[LifeEventAgent] session={session} no life event detected")
    return {**state, "is_life_event": False}


def route_after_life_event_check(state: JanSathiState) -> str:
    """
    Conditional edge: if life event detected → skip full pipeline, go to response.
    Otherwise → normal intent classification.
    """
    if state.get("is_life_event"):
        return "response_agent"
    return "intent_agent"
