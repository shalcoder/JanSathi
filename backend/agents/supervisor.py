"""
supervisor.py — JanSathi LangGraph StateGraph Orchestrator
===========================================================
Wires all 9 agent nodes into a compiled LangGraph graph.

Flow:
  START
    ↓
  telecom_agent       ← consent gate
    ↓ (conditional: END if no consent)
  intent_agent        ← classify intent + detect scheme
    ↓
  rag_agent           ← retrieve knowledge
    ↓
  slot_collection_agent  ← collect user profile (may return early for more slots)
    ↓ (conditional: loop back or proceed)
  rules_agent         ← deterministic eligibility (no LLM)
    ↓
  verifier_agent      ← risk scoring + routing decision
    ↓ (conditional)
    ├─ AUTO_SUBMIT/NOT_ELIGIBLE → response_agent → notification_agent → END
    └─ HITL_QUEUE              → hitl_agent → notification_agent → END
"""
import logging
from typing import Literal

try:
    from langgraph.graph import StateGraph, END, START
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from .state import JanSathiState, initial_state
from .telecom_agent import telecom_agent, should_continue_after_telecom
from .intent_agent import intent_agent
from .rag_agent import rag_agent
from .slot_collection_agent import slot_collection_agent, should_continue_slot_collection
from .rules_agent import rules_agent
from .verifier_agent import verifier_agent, should_route_after_verifier
from .response_agent import response_agent
from .notification_agent import notification_agent
from .hitl_agent import hitl_agent

logger = logging.getLogger(__name__)


def create_graph():
    """
    Build and compile the JanSathi LangGraph StateGraph.
    Returns a compiled graph ready for invoke().
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError(
            "langgraph is not installed. Run: pip install langgraph>=0.2.0"
        )

    graph = StateGraph(JanSathiState)

    # ── Register all 9 agent nodes ────────────────────────────────────────────
    graph.add_node("telecom_agent",          telecom_agent)
    graph.add_node("intent_agent",           intent_agent)
    graph.add_node("rag_agent",              rag_agent)
    graph.add_node("slot_collection_agent",  slot_collection_agent)
    graph.add_node("rules_agent",            rules_agent)
    graph.add_node("verifier_agent",         verifier_agent)
    graph.add_node("response_agent",         response_agent)
    graph.add_node("hitl_agent",             hitl_agent)
    graph.add_node("notification_agent",     notification_agent)

    # ── Entry point ───────────────────────────────────────────────────────────
    graph.set_entry_point("telecom_agent")

    # ── Edge 1: Consent gate ──────────────────────────────────────────────────
    graph.add_conditional_edges(
        "telecom_agent",
        should_continue_after_telecom,
        {
            "intent_agent": "intent_agent",
            "__end__": END,
        },
    )

    # ── Edge 2: Intent → RAG (always) ────────────────────────────────────────
    graph.add_edge("intent_agent", "rag_agent")

    # ── Edge 3: RAG → Slot Collection ────────────────────────────────────────
    graph.add_edge("rag_agent", "slot_collection_agent")

    # ── Edge 4: Slot collection loop gate ────────────────────────────────────
    # If slots incomplete → END early (client re-invokes with user's answer)
    # If slots complete  → rules_agent
    graph.add_conditional_edges(
        "slot_collection_agent",
        should_continue_slot_collection,
        {
            "rules_agent": "rules_agent",
            "__end__": END,
        },
    )

    # ── Edge 5: Rules → Verifier ──────────────────────────────────────────────
    graph.add_edge("rules_agent", "verifier_agent")

    # ── Edge 6: Verifier routing ──────────────────────────────────────────────
    graph.add_conditional_edges(
        "verifier_agent",
        should_route_after_verifier,
        {
            "response_agent": "response_agent",
            "hitl_agent":     "hitl_agent",
        },
    )

    # ── Edge 7: Response → Notification ──────────────────────────────────────
    graph.add_edge("response_agent", "notification_agent")

    # ── Edge 8: HITL → Notification ──────────────────────────────────────────
    graph.add_edge("hitl_agent", "notification_agent")

    # ── Edge 9: Notification → END ────────────────────────────────────────────
    graph.add_edge("notification_agent", END)

    # Compile graph
    compiled = graph.compile()
    logger.info("[Supervisor] JanSathi LangGraph compiled successfully")
    return compiled


# ── Singleton compiled graph ──────────────────────────────────────────────────
_compiled_graph = None


def get_graph():
    """Get or create the singleton compiled graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = create_graph()
    return _compiled_graph


def run_pipeline(
    session_id: str,
    user_query: str,
    channel: str = "web",
    language: str = "hi",
    phone: str = "",
    consent_given: bool = True,
    slots: dict = None,
    asr_confidence: float = 1.0,
    existing_state: dict = None,
) -> JanSathiState:
    """
    High-level entry point to run the JanSathi agent pipeline.

    Args:
        session_id:     Unique session identifier
        user_query:     Current user message (text or IVR transcript)
        channel:        "web" | "ivr" | "sms"
        language:       "hi" | "en" | "ta" | ...
        phone:          User phone number (for SMS notifications)
        consent_given:  Whether user has given data consent
        slots:          Previously collected slot values (for multi-turn)
        asr_confidence: ASR confidence score (1.0 for text, 0-1 for IVR audio)
        existing_state: Carry over state from previous turn (multi-turn conversations)

    Returns:
        Final JanSathiState after the pipeline completes
    """
    graph = get_graph()

    # ── Build initial state ───────────────────────────────────────────────────
    if existing_state:
        # Multi-turn: carry over existing state, update with new query
        state = dict(existing_state)
        state["user_query"] = user_query
        state["session_id"] = session_id
    else:
        state = initial_state(
            session_id=session_id,
            channel=channel,
            language=language,
            user_query=user_query,
            phone=phone,
            asr_confidence=asr_confidence,
        )

    # Apply caller-provided values
    state["consent_given"] = consent_given
    if slots:
        state["slots"] = {**state.get("slots", {}), **slots}

    logger.info(
        f"[Supervisor] Starting pipeline: session={session_id} "
        f"channel={channel} lang={language} intent_hint=none"
    )

    try:
        final_state = graph.invoke(state)
        logger.info(
            f"[Supervisor] Pipeline complete: session={session_id} "
            f"intent={final_state.get('intent')} "
            f"decision={final_state.get('verifier_result', {}).get('decision', 'N/A')}"
        )
        return final_state
    except Exception as e:
        logger.error(f"[Supervisor] Pipeline error: {e}")
        error_state = dict(state)
        error_state["error"] = str(e)
        error_state["response_text"] = (
            "⚠️ JanSathi encountered an issue. Please try again or visit india.gov.in"
        )
        return error_state


def run_pipeline_fallback(
    session_id: str,
    user_query: str,
    channel: str = "web",
    language: str = "hi",
) -> JanSathiState:
    """
    Fallback pipeline (when LangGraph is unavailable).
    Runs agents sequentially without the graph framework.
    """
    logger.warning("[Supervisor] Running fallback sequential pipeline (no LangGraph)")

    state = initial_state(
        session_id=session_id,
        channel=channel,
        language=language,
        user_query=user_query,
    )
    state["consent_given"] = True

    try:
        state = telecom_agent(state)
        if not state.get("consent_given"):
            return state
        state = intent_agent(state)
        state = rag_agent(state)
        state = slot_collection_agent(state)
        if not state.get("slots_complete"):
            return state  # Return with question
        state = rules_agent(state)
        state = verifier_agent(state)
        decision = state.get("verifier_result", {}).get("decision", "AUTO_SUBMIT")
        if decision == "HITL_QUEUE":
            state = hitl_agent(state)
        else:
            state = response_agent(state)
        state = notification_agent(state)
    except Exception as e:
        logger.error(f"[Supervisor] Fallback pipeline error: {e}")
        state["error"] = str(e)
        state["response_text"] = "⚠️ System error. Please visit india.gov.in"

    return state
