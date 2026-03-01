"""
execution.py — JanSathi Agentic Execution Layer (Round 2)

This module is the ONLY entry point for all transport layers (Web, IVR, WhatsApp).
It wires together:
  1. IntentService       → classify what the user wants + which scheme
  2. AgenticWorkflowEngine → FSM slot collection + deterministic rule evaluation
  3. BedrockService      → LLM grievance draft (if intent == grievance)
  4. ReceiptService       → generate HTML receipt + S3 upload (on workflow completion)
  5. NotifyService        → log SMS dispatch event

BEFORE THIS CHANGE: process_user_input() sent raw text → FSM directly.
  - "PM Kisan" spoken ≠ "start_apply:pm_kisan" literal → FSM never routed.
  - BedrockService existed but was never called here.
  - ReceiptService existed but was never called here.

AFTER THIS CHANGE:
  - EVERY call goes through IntentService.classify() first.
  - If intent is "apply"  → route to correct scheme FSM via start_apply:<scheme_hint>
  - If intent is "grievance" → use Bedrock to draft a formal grievance, or FSM fallback
  - If intent is "track"  → route to track_status command
  - Otherwise             → let the FSM handle it (ongoing slot collection / general)
  - On terminal FSM states (ELIGIBLE / NOT_ELIGIBLE / COMPLETED)
    → call ReceiptService to generate real HTML receipt
"""

import os
import json
import logging
import uuid
from typing import Dict

from agentic_engine.storage import LocalJSONStorage, DynamoDBStorage
from agentic_engine.session_manager import SessionManager
from agentic_engine.workflow_engine import AgenticWorkflowEngine

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ── Engine singleton ────────────────────────────────────────────────────────────

_engine = None
_init_error = None


def initialize_engine():
    global _engine, _init_error
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    try:
        if storage_type == "local":
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            session_file = os.path.join(base_dir, "agentic_engine", "sessions.json")
            storage = LocalJSONStorage(session_file)
        elif storage_type == "dynamodb":
            table_name = os.getenv("DYNAMODB_TABLE", "JanSathiSessions")
            region = os.getenv("AWS_REGION", "us-east-1")
            storage = DynamoDBStorage(table_name=table_name, region_name=region)
        else:
            raise ValueError(f"Unsupported STORAGE_TYPE: {storage_type}")
        session_manager = SessionManager(storage)
        _engine = AgenticWorkflowEngine(session_manager)
        _init_error = None
        return _engine
    except Exception as e:
        _init_error = str(e)
        logger.error(f"[Execution] Failed to initialize engine: {_init_error}")
        _engine = None
        return None


initialize_engine()


# ── Intent → FSM command mapper ─────────────────────────────────────────────────

# Map scheme_hint → FSM scheme key (from schemes_config.yaml)
SCHEME_HINT_MAP = {
    "pm_kisan":      "pm_kisan",
    "pm_awas_urban": "pm_awas_urban",
    "pm_awas":       "pm_awas_urban",
    "e_shram":       "e_shram",
    "eshram":        "e_shram",
    "unknown":       "pm_kisan",   # default
}

# Keyword → scheme override (if Bedrock not available)
SCHEME_KEYWORD_MAP = {
    "awas":    "pm_awas_urban",
    "housing": "pm_awas_urban",
    "kisan":   "pm_kisan",
    "किसान":  "pm_kisan",
    "farmer":  "pm_kisan",
    "shram":   "e_shram",
    "worker":  "e_shram",
    "labour":  "e_shram",
    "श्रम":   "e_shram",
}


def _detect_scheme(message: str, scheme_hint: str) -> str:
    """Detect scheme from hint or keyword fallback."""
    if scheme_hint and scheme_hint != "unknown":
        return SCHEME_HINT_MAP.get(scheme_hint, "pm_kisan")
    msg = message.lower()
    for kw, scheme in SCHEME_KEYWORD_MAP.items():
        if kw in msg:
            return scheme
    return "pm_kisan"


def _is_ongoing_slot_collection(session_id: str) -> bool:
    """Return True if the session is currently mid-slot-collection."""
    if _engine is None:
        return False
    try:
        sm = _engine.session_manager
        session = sm.get_session(session_id)
        if not session:
            return False
        state = session.get("current_state", "")
        return state in ("COLLECT_SLOTS", "COLLECT_STATE", "COLLECT_LAND_OWNERSHIP")
    except Exception:
        return False


def _generate_receipt(result: dict, session_id: str, scheme_name: str, language: str) -> dict:
    """Call ReceiptService to generate real HTML receipt. Returns receipt dict or {}."""
    benefit_receipt = result.get("benefit_receipt") or {}
    if not benefit_receipt:
        return {}
    try:
        from app.services.receipt_service import ReceiptService
        eligible = benefit_receipt.get("eligible", False)
        rules_trace = benefit_receipt.get("rules", [])
        rules_score = float(benefit_receipt.get("confidence", 0.85))

        # Build slot snapshot for receipt
        session_data = result.get("session_data", {})
        slots = {k: v for k, v in session_data.items() if not k.startswith("_")}

        receipt = ReceiptService().generate_receipt(
            session_id=session_id,
            scheme_name=scheme_name,
            eligible=eligible,
            rules_trace=rules_trace,
            rules_score=rules_score,
            slots=slots,
            language=language,
        )
        logger.info(f"[Execution] Receipt generated: {receipt.get('case_id')} eligible={eligible}")
        return receipt
    except Exception as e:
        logger.warning(f"[Execution] ReceiptService failed (non-fatal): {e}")
        return {}


def _draft_grievance_with_llm(session_id: str, user_text: str, session_data: dict, language: str) -> dict:
    """
    Use BedrockService to generate a formal grievance letter.
    Falls back to structured template if Bedrock is unavailable.
    """
    import random
    import string
    grievance_id = "GRV-" + "".join(random.choices(string.digits, k=6))

    # Try Bedrock first
    try:
        from app.services.bedrock_service import BedrockService
        from app.services.rag_service import RagService

        rag = RagService()
        context = rag.retrieve_context(f"PM-Kisan grievance process {user_text}", language)

        context_text = " ".join(context) if isinstance(context, list) else str(context)

        bedrock = BedrockService()
        if bedrock.working:
            state = session_data.get("state", "the applicant's district")
            scheme = session_data.get("_scheme", "PM-Kisan Samman Nidhi")
            prompt = (
                f"Draft a formal grievance application letter for a citizen from {state} "
                f"regarding: '{user_text}'. "
                f"The scheme is '{scheme}'. "
                f"The grievance reference number is {grievance_id}. "
                f"Tone: formal, Hindi if language='hi', English otherwise. "
                f"Structure: Subject line, body (3 paragraphs), closing. "
                f"Context from official sources: {context_text[:500]}"
            )
            result = bedrock.generate_response(
                query=prompt,
                context_text=context_text,
                language=language,
                intent="GRIEVANCE_DRAFT"
            )
            draft_text = result.get("text", "")
            if draft_text:
                return {
                    "grievance_id": grievance_id,
                    "draft_text": draft_text,
                    "method": "llm",
                    "scheme": scheme,
                }
    except Exception as e:
        logger.warning(f"[Execution] Bedrock grievance draft failed, using template: {e}")

    # Template fallback
    state = session_data.get("state", "applicant's district")
    draft_text = (
        f"To,\nThe District Grievance Officer,\n{state.title()} District\n\n"
        f"Subject: Grievance Regarding Government Scheme Payment — Ref: {grievance_id}\n\n"
        f"Respected Sir/Madam,\n\n"
        f"I am writing to formally register a grievance regarding: {user_text}. "
        f"Despite fulfilling all eligibility criteria, I have not received the entitled benefit. "
        f"I respectfully request an urgent review and resolution of this matter.\n\n"
        f"Grievance Reference No.: {grievance_id}\n\n"
        f"Yours faithfully,\n[Applicant Name]"
    )
    return {
        "grievance_id": grievance_id,
        "draft_text": draft_text,
        "method": "template",
        "scheme": session_data.get("_scheme", "Government Scheme"),
    }


# ── Primary entry point ─────────────────────────────────────────────────────────

def process_user_input(message: str, session_id: str, language: str = "hi",
                       user_profile: dict = None, channel: str = "web") -> dict:
    """
    Real agentic execution pipeline:
    1. Validate inputs
    2. Classify intent via IntentService (Bedrock if available, keyword fallback)
    3. Route:
       a. DTMF / literal commands → FSM directly
       b. "apply" intent → start_apply:<scheme> if new session, else continue slots
       c. "grievance" intent → draft via Bedrock LLM
       d. "track" intent     → track_status command
       e. ongoing slots      → pass answer to FSM
       f. fallback / info    → FSM (will use RAG-based response)
    4. On terminal FSM state → generate real HTML receipt
    5. Return enriched response dict
    """
    user_profile = user_profile or {}

    # ── 1. Validation ───────────────────────────────────────────────────────────
    if not session_id or not isinstance(session_id, str):
        return {"error": "Invalid session_id", "action_type": "ERROR",
                "response": "Internal System Error: Session ID missing."}
    if message is None:
        message = ""

    # ── 2. Engine check ─────────────────────────────────────────────────────────
    if _engine is None:
        initialize_engine()
    if _engine is None:
        return {"error": "Engine Not Initialized", "action_type": "ERROR",
                "response": f"Internal System Error: {_init_error or 'Engine offline.'}"}

    # ── 3. DTMF / special commands pass straight through ── ────────────────────
    is_dtmf = message.startswith("DTMF:")
    is_literal_cmd = any(message.lower().startswith(p) for p in
                         ("start_apply:", "grievance:", "track_status", "restart"))

    if is_dtmf or is_literal_cmd:
        logger.info(f"[Execution] Literal command → FSM: {message[:40]}")
        try:
            result = _engine.handle_input(session_id=session_id, user_input=message)
            return _enrich_result(result, session_id, language, scheme_name=None)
        except Exception as e:
            logger.error(f"[Execution] FSM error: {e}")
            return _error_resp(e)

    # ── 4. Ongoing slot collection → pass answer to FSM directly ───────────────
    if _is_ongoing_slot_collection(session_id):
        logger.info(f"[Execution] Slot collection ongoing → forwarding to FSM")
        try:
            result = _engine.handle_input(session_id=session_id, user_input=message)
            sm = _engine.session_manager
            session = sm.get_session(session_id)
            scheme_name = (session or {}).get("data", {}).get("_scheme", "pm_kisan")
            return _enrich_result(result, session_id, language, scheme_name=scheme_name)
        except Exception as e:
            logger.error(f"[Execution] FSM slot error: {e}")
            return _error_resp(e)

    # ── 5. Intent classification ─────────────────────────────────────────────────
    intent_result = {"intent": "info", "confidence": 0.6, "scheme_hint": "unknown"}
    try:
        from app.services.intent_service import IntentService
        svc = IntentService()
        # Use IVR-aware classify so language is passed to Bedrock classifier
        classified = svc.classifier.classify(message, language)
        validated = svc._validate(classified)
        intent_result = validated
        logger.info(f"[Execution] Intent: {intent_result['intent']} | confidence: {intent_result.get('confidence'):.2f} | scheme: {intent_result.get('scheme_hint')}")
    except Exception as e:
        logger.warning(f"[Execution] IntentService failed, defaulting to info: {e}")

    intent = intent_result.get("intent", "info")
    scheme_hint = intent_result.get("scheme_hint", "unknown")
    scheme_name = _detect_scheme(message, scheme_hint)

    # ── 6. Route by intent ───────────────────────────────────────────────────────

    # ── 6a. GRIEVANCE → LLM draft ───────────────────────────────────────────────
    if intent == "grievance":
        logger.info(f"[Execution] Grievance intent → Bedrock draft")
        try:
            sm = _engine.session_manager
            session = sm.get_session(session_id) or sm.create_session(session_id)
            session_data = session.get("data", {})

            grievance = _draft_grievance_with_llm(session_id, message, session_data, language)
            grievance_id = grievance["grievance_id"]

            # Store in session
            sm.update_data(session_id, "grievance_id", grievance_id)
            sm.update_data(session_id, "grievance_draft", grievance["draft_text"])

            response_text = (
                f"आपकी शिकायत दर्ज की गई है। शिकायत ID: {grievance_id}\n\n"
                f"{grievance['draft_text'][:300]}...\n\nकृपया अपने नजदीकी CSC केंद्र पर इसे जमा करें।"
                if language == "hi"
                else
                f"Grievance registered. ID: {grievance_id}\n\n"
                f"Draft: {grievance['draft_text'][:300]}...\n\nVisit your nearest CSC to submit."
            )
            return {
                "response": response_text,
                "response_text": response_text,
                "current_state": "GRIEVANCE_SUBMITTED",
                "action_type": "GRIEVANCE_SUBMITTED",
                "is_terminal": True,
                "requires_input": False,
                "session_data": {"grievance_id": grievance_id, "draft_text": grievance["draft_text"]},
                "grievance": grievance,
                "artifact": {
                    "type": "grievance",
                    "grievance_id": grievance_id,
                    "draft": grievance["draft_text"],
                    "method": grievance.get("method"),
                },
                "sms_payload": {
                    "to": "masked",
                    "body": f"JanSathi: Grievance {grievance_id} registered. Our team will respond within 24 hours."
                }
            }
        except Exception as e:
            logger.error(f"[Execution] Grievance pipeline failed: {e}")
            return _error_resp(e)

    # ── 6b. TRACK → track_status ─────────────────────────────────────────────────
    if intent == "track":
        logger.info(f"[Execution] Track intent → FSM track_status")
        try:
            result = _engine.handle_input(session_id=session_id, user_input="track_status")
            return _enrich_result(result, session_id, language, scheme_name=None)
        except Exception as e:
            return _error_resp(e)

    # ── 6c. APPLY → start_apply:<scheme> ─────────────────────────────────────────
    if intent == "apply":
        logger.info(f"[Execution] Apply intent → start_apply:{scheme_name}")
        try:
            result = _engine.handle_input(session_id=session_id, user_input=f"start_apply:{scheme_name}")
            return _enrich_result(result, session_id, language, scheme_name=scheme_name)
        except Exception as e:
            return _error_resp(e)

    # ── 6d. INFO / FALLBACK → send to FSM (which will do RAG if connected) ──────
    logger.info(f"[Execution] Info/fallback intent → FSM + RAG")
    try:
        result = _engine.handle_input(session_id=session_id, user_input=message)
        return _enrich_result(result, session_id, language, scheme_name=scheme_name)
    except Exception as e:
        return _error_resp(e)


# ── Helper: enrich FSM result with receipt if terminal ─────────────────────────

def _enrich_result(result: dict, session_id: str, language: str, scheme_name: str | None) -> dict:
    """
    After FSM returns: if this is a terminal ELIGIBLE state,
    call ReceiptService and attach the real receipt URL + checklist.
    """
    if not result:
        return result

    action = result.get("action_type", "")
    state = result.get("current_state", "")
    is_terminal = result.get("is_terminal", False)

    benefit_receipt = result.get("benefit_receipt")

    # Detect eligibility terminal state
    is_eligibility_result = (
        benefit_receipt is not None or
        action in ("ELIGIBILITY_RESULT",) or
        state in ("ELIGIBLE_CONFIRMED",)
    )

    if is_eligibility_result and scheme_name:
        receipt = _generate_receipt(result, session_id, scheme_name, language)
        if receipt:
            result["receipt"] = receipt
            result["artifact_generated"] = {
                "type": "receipt",
                "case_id": receipt.get("case_id"),
                "url": receipt.get("receipt_url"),
                "eligible": receipt.get("eligible"),
                "scheme_name": receipt.get("scheme_name"),
                "document_checklist": receipt.get("document_checklist"),
            }
            result["sms_payload"] = {
                "to": "masked",
                "body": (
                    f"JanSathi: Case {receipt['case_id']} — "
                    f"{'ELIGIBLE ✅' if receipt.get('eligible') else 'NOT ELIGIBLE ❌'} for "
                    f"{receipt.get('scheme_name', 'scheme')}. "
                    f"Receipt: {receipt.get('receipt_url', 'https://jansathi.gov.in')}"
                )
            }

    # Attempt SMS log (best-effort)
    if is_terminal:
        try:
            from app.services.notify_service import NotifyService
            NotifyService().log_event(session_id=session_id, event_type=action, data=result.get("session_data", {}))
        except Exception:
            pass

    return result


def _error_resp(e: Exception) -> dict:
    return {
        "error": str(type(e).__name__),
        "details": str(e),
        "action_type": "ERROR",
        "response": "मुझे एक त्रुटि आई है। कृपया पुनः प्रयास करें। / An error occurred. Please try again.",
    }
