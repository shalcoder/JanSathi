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
            state = session_data.get("state", session_data.get("district", "the applicant's district"))
            scheme = session_data.get("_scheme", "PM-Kisan Samman Nidhi")
            app_id = session_data.get("application_id", "Not Provided")
            last_pay = session_data.get("last_payment_date", "Not Provided")
            prompt = (
                f"Draft a formal grievance application letter for a citizen from {state} "
                f"regarding: '{user_text}'. "
                f"Application ID: {app_id}. Last Payment Date: {last_pay}. "
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


def _upload_text_to_s3(doc_id: str, text: str, folder="grievances") -> str:
    try:
        import boto3
        from botocore.config import Config
        region = os.getenv("AWS_REGION", "ap-south-1")
        bucket = os.getenv("RECEIPT_BUCKET", "jansathi-receipts")
        s3 = boto3.client("s3", region_name=region, config=Config(signature_version="s3v4"))
        key = f"{folder}/{doc_id}.txt"
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=text.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
        )
        return s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=604800
        )
    except Exception as e:
        logger.warning(f"[Execution] S3 text upload failed: {e}")
        return f"https://jansathi.example.com/{folder}/{doc_id}"

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
        print(f"DEBUG: Classified message: {message} with language {language}", flush=True)
        classified = svc.classifier.classify(message, language)
        print(f"DEBUG: Intent result: {classified}", flush=True)
        validated = svc._validate(classified)
        intent_result = validated
        logger.info(f"[Execution] Intent: {intent_result['intent']} | confidence: {intent_result.get('confidence'):.2f} | scheme: {intent_result.get('scheme_hint')}")
    except Exception as e:
        logger.warning(f"[Execution] IntentService failed, defaulting to info: {e}")

    intent = intent_result.get("intent", "info")
    scheme_hint = intent_result.get("scheme_hint", "unknown")
    event_key = intent_result.get("event_key", "unknown")
    scheme_name = _detect_scheme(message, scheme_hint)

    # ── 6. Route by intent ───────────────────────────────────────────────────────

    # ── 6a. LIFE_EVENT → civic orchestration case ───────────────────────────────
    if intent == "life_event":
        logger.info(f"[Execution] Life event intent → create life-event case ({event_key})")
        try:
            from app.services.civic_infra_service import CivicInfraService
            user_id = user_profile.get("id") or user_profile.get("user_id") or "anonymous"
            case = CivicInfraService().create_life_event_case(
                session_id=session_id,
                event_key=event_key if event_key != "unknown" else "crop_loss",
                user_id=user_id,
                language=language,
            )
            response_text = (
                f"Life-event workflow started: {case.get('event_label', 'Civic Workflow')}. "
                f"Case ID {case.get('case_id')}. Step 1 is now active."
            )
            return {
                "response": response_text,
                "response_text": response_text,
                "action_type": "LIFE_EVENT_CASE_STARTED",
                "current_state": "LIFE_EVENT_IN_PROGRESS",
                "is_terminal": False,
                "requires_input": True,
                "session_data": {},
                "life_event_case": case,
                "telemetry": {
                    "intent": "life_event",
                    "event_key": event_key,
                    "confidence": intent_result.get("confidence", 0.9),
                },
            }
        except Exception as e:
            logger.error(f"[Execution] Life event orchestration failed: {e}")
            return _error_resp(e)

    # ── 6b. GRIEVANCE → LLM draft ───────────────────────────────────────────────
    if intent == "grievance":
        logger.info(f"[Execution] Grievance intent → Starting slot collection")
        try:
            scheme_to_use = f"grievance_{scheme_name}" if scheme_name != "unknown" else "grievance_pm_kisan"
            result = _engine.handle_input(session_id=session_id, user_input=f"start_apply:{scheme_to_use}")
            return _enrich_result(result, session_id, language, scheme_name=scheme_to_use)
        except Exception as e:
            logger.error(f"[Execution] Grievance pipeline failed: {e}")
            return _error_resp(e)

    # ── 6c. TRACK → track_status ─────────────────────────────────────────────────
    if intent == "track":
        logger.info(f"[Execution] Track intent → FSM track_status")
        try:
            result = _engine.handle_input(session_id=session_id, user_input="track_status")
            return _enrich_result(result, session_id, language, scheme_name=None)
        except Exception as e:
            return _error_resp(e)

    # ── 6d. APPLY → start_apply:<scheme> ─────────────────────────────────────────
    if intent == "apply":
        logger.info(f"[Execution] Apply intent → start_apply:{scheme_name}")
        try:
            result = _engine.handle_input(session_id=session_id, user_input=f"start_apply:{scheme_name}")
            return _enrich_result(result, session_id, language, scheme_name=scheme_name)
        except Exception as e:
            return _error_resp(e)

    # ── 6e. INFO / FALLBACK → Smart RAG Pipeline ──────────────────────────────
    logger.info(f"[Execution] Info/fallback intent → Smart RAG Pipeline")
    try:
        from app.services.smart_rag_service import SmartRAGService
        
        smart_rag = SmartRAGService()
        rag_result = smart_rag.query(
            user_query=message,
            language=language,
            user_profile=user_profile,
            session_id=session_id
        )
        
        # Build response in FSM format
        response_text = rag_result['answer']
        
        # Add learning indicator if this was a new answer
        if rag_result.get('learned'):
            learning_note = "\n\n💡 This answer has been added to our knowledge base for future queries." if language == 'en' else "\n\n💡 यह उत्तर भविष्य के प्रश्नों के लिए हमारे ज्ञान आधार में जोड़ दिया गया है।"
            response_text += learning_note
        
        # Format result to match FSM structure
        result = {
            "response": response_text,
            "response_text": response_text,
            "action_type": "INFORMATION_PROVIDED",
            "current_state": "INFO_QUERY",
            "is_terminal": False,
            "requires_input": True,
            "session_data": {},
            "telemetry": {
                "intent": "information",
                "confidence": rag_result['confidence'],
                "source": rag_result['source'],
                "learned": rag_result.get('learned', False),
                **rag_result.get('telemetry', {})
            },
            "sources": rag_result.get('sources', []),
        }
        
        logger.info(f"[SmartRAG] Source: {rag_result['source']} | Confidence: {rag_result['confidence']:.2f} | Learned: {rag_result.get('learned', False)}")
        
        return _enrich_result(result, session_id, language, scheme_name=scheme_name)
        
    except Exception as e:
        logger.warning(f"[SmartRAG] Failed, falling back to FSM: {e}")
        # Fallback to original FSM behavior
        try:
            print("DEBUG: Calling engine.handle_input...", flush=True)
            result = _engine.handle_input(session_id=session_id, user_input=message)
            print("DEBUG: engine.handle_input finished.", flush=True)
            return _enrich_result(result, session_id, language, scheme_name=scheme_name)
        except Exception as e2:
            return _error_resp(e2)


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
            
    # Handle Grievance Terminal State
    if is_terminal and state == "READY_FOR_GRIEVANCE":
        sm = _engine.session_manager
        session = sm.get_session(session_id)
        session_data = session.get("data", {})
        
        # User goal is tracked in intent maybe? or just use a generic message
        user_text = session_data.get("_last_message", "Non-receipt of payment")
        
        grievance = _draft_grievance_with_llm(session_id, user_text, session_data, language)
        grievance_id = grievance["grievance_id"]
        
        sm.update_data(session_id, "grievance_id", grievance_id)
        sm.update_data(session_id, "grievance_draft", grievance["draft_text"])
        
        doc_url = _upload_text_to_s3(grievance_id, grievance["draft_text"], folder="grievances")
        
        response_text = (
            f"आपकी शिकायत दर्ज कर ली गई है। शिकायत आईडी: {grievance_id}\n\nकृपया अपने रिकॉर्ड के लिए रसीद डाउनलोड करें।"
            if language == "hi"
            else
            f"Grievance registered. ID: {grievance_id}\n\nPlease download your draft receipt."
        )
        result.update({
            "response": response_text,
            "response_text": response_text,
            "current_state": "GRIEVANCE_SUBMITTED",
            "action_type": "GRIEVANCE_SUBMITTED",
            "is_terminal": True,
            "requires_input": False,
            "artifact_generated": {
                "type": "grievance",
                "url": doc_url,
                "case_id": grievance_id,
            },
            "sms_payload": {
                "to": "masked",
                "body": f"JanSathi: Grievance {grievance_id} registered. Draft: {doc_url}"
            }
        })

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
