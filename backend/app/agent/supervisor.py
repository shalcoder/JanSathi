"""
supervisor.py — JanSathi 9-Agent Orchestrator

Linear flow (per agents.md & userflow.md — deterministic, not AI drama):

  [1] Telecom Entry Agent   (connect_webhook / process_user_input)
      ↓
  [2] Intent Classification Agent  (intent_service)
      ↓
  [3] Scheme Retrieval Agent —INFORMATION path— (rag_service)
  OR
  [4] Slot Collection Agent  (ivr_service + workflow_engine)
      ↓
  [5] Deterministic Rules Agent  (rules_engine)
      ↓
  [6] Verifier & Risk Agent  (verifier_service)
      ↓
  [7] Workflow Orchestration Agent  (workflow_service / Step Functions)
      ↓
  [8] Notification Agent  (notify_service)
      +
  [9] HITL Agent  (hitl_service)  — only if Verifier says HITL_QUEUE

Design principles (idea.md):
  - Rules agent **always** overrides LLM outputs on eligibility
  - No portal scraping, no auto-submission
  - Consent must be captured before any PII collection
  - Audit log written at every decision boundary
"""

import uuid
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Lazy service registry (avoids circular imports + cold-start cost) ─────────

def _intent():
    from app.services.intent_service import IntentService
    return IntentService()

def _verifier():
    from app.services.verifier_service import VerifierService
    return VerifierService()

def _hitl():
    from app.services.hitl_service import HITLService
    return HITLService()

def _notify():
    from app.services.notify_service import NotifyService
    return NotifyService()

def _receipt():
    from app.services.receipt_service import ReceiptService
    return ReceiptService()

def _audit():
    from app.services.audit_service import AuditService
    return AuditService()

def _telemetry():
    from app.services.telemetry_service import get_telemetry
    return get_telemetry()

def _rules():
    from app.services.rules_engine import RulesEngine
    return RulesEngine()

def _rag():
    from app.services.rag_service import RagService
    return RagService()

def _workflow():
    from app.services.workflow_service import WorkflowService
    return WorkflowService()

def _engine():
    from app.core.execution import process_user_input
    return process_user_input


# ─────────────────────────────────────────────────────────────────────────────
class JanSathiSupervisor:
    """
    Central orchestrator for JanSathi's 9-agent pipeline.
    Single entry point for all channels (IVR, web, WhatsApp).
    """

    # ── Public entry points ───────────────────────────────────────────────────

    def orchestrate(self, event: dict) -> dict:
        """
        Universal entry point. Routes by channel then runs unified pipeline.

        event keys:
          session_id  str   (required)
          message     str   transcript / user text
          language    str   'hi' | 'ta' | 'en' (default 'hi')
          channel     str   'ivr' | 'web' | 'whatsapp' (default 'web')
          consent     bool  whether user has given consent (required for PII)
          asr_confidence float  (IVR only, 0-1)
          turn_id     str   optional
          slots       dict  any pre-collected slots to seed
        """
        t_start = time.perf_counter()
        session_id     = event.get("session_id") or f"sess-{uuid.uuid4().hex[:10]}"
        message        = event.get("message", "").strip()
        language       = event.get("language", "hi")
        channel        = event.get("channel", "web")
        consent        = event.get("consent", True)   # web implies consent
        asr_confidence = float(event.get("asr_confidence", 1.0))
        turn_id        = event.get("turn_id") or str(uuid.uuid4())
        pre_slots      = event.get("slots", {})

        tel = _telemetry()

        logger.info(f"[Supervisor] session={session_id} channel={channel} lang={language}")

        # ── 0. Consent gate (IVR mandatory) ─────────────────────────────────
        if channel == "ivr" and not consent:
            return self._play_prompt(
                "कृपया सहमति दें। Press 1 to consent.",   # Consent required
                session_id, turn_id, "CONSENT_REQUIRED",
                requires_input=True
            )

        # ── Audit: log consent ───────────────────────────────────────────────
        try:
            caller_hash = str(hash(session_id))[:16]
            _audit().log_consent(session_id, caller_hash, language, consent)
        except Exception as e:
            logger.warning(f"[Supervisor] Audit consent failed: {e}")

        if not message:
            return self._play_prompt(
                "नमस्ते! जनसाथी में आपका स्वागत है। आप किस योजना के बारे में जानना चाहते हैं?",
                session_id, turn_id, "GREETING", requires_input=True
            )

        # ── [2] INTENT CLASSIFICATION AGENT ─────────────────────────────────
        try:
            t_intent = time.perf_counter()
            intent_result = _intent().classify_intent_ivr(message, language)
            tel.emit_latency("BedrockLatencyMs", t_intent, {"agent": "intent"})

            intent      = intent_result.get("intent", "INFORMATION")
            intent_conf = float(intent_result.get("confidence", 0.75))
            scheme_hint = intent_result.get("scheme_hint", "pm_kisan")
            lang_det    = intent_result.get("language_detected", language)
        except Exception as e:
            logger.error(f"[Supervisor] Intent agent error: {e}")
            intent      = "INFORMATION"
            intent_conf = 0.6
            scheme_hint = "pm_kisan"
            lang_det    = language

        # Normalise intent to agents.md spec
        intent = self._normalise_intent(intent)

        # Audit turn
        try:
            _audit().log_turn(session_id, turn_id, message, intent, intent_conf, asr_confidence)
        except Exception:
            pass

        # Clarify if confidence too low
        if intent_conf < 0.60:
            return self._play_prompt(
                "माफ़ कीजिए, मैं समझ नहीं पाया। क्या आप PM-Kisan आवेदन, जानकारी, या शिकायत चाहते हैं?",
                session_id, turn_id, "CLARIFY", requires_input=True
            )

        logger.info(f"[Supervisor] intent={intent} scheme={scheme_hint} conf={intent_conf:.2f}")

        # ── [3] SCHEME RETRIEVAL AGENT (INFORMATION path) ────────────────────
        if intent == "INFORMATION":
            return self._handle_information(session_id, turn_id, message, language, lang_det, t_start)

        # ── [4] SLOT COLLECTION AGENT (APPLY_SCHEME path) ────────────────────
        if intent == "APPLY_SCHEME":
            return self._handle_apply(
                session_id, turn_id, message, lang_det, scheme_hint,
                asr_confidence, intent_conf, pre_slots, channel, t_start
            )

        # ── CHECK_STATUS path ────────────────────────────────────────────────
        if intent == "CHECK_STATUS":
            return self._handle_status(session_id, turn_id, lang_det, t_start)

        # ── GRIEVANCE path ───────────────────────────────────────────────────
        if intent == "GRIEVANCE":
            return self._handle_grievance(session_id, turn_id, message, lang_det, t_start)

        # ── Fallback ─────────────────────────────────────────────────────────
        return self._play_prompt(
            "मैं आपकी मदद के लिए यहाँ हूँ। PM-Kisan, PM Awas, या E-Shram के बारे में पूछें।",
            session_id, turn_id, "FALLBACK", requires_input=True
        )

    # ── APPLY flow (agents 4→5→6→7→8→9) ─────────────────────────────────────

    def _handle_apply(
        self, session_id, turn_id, message, language, scheme_name,
        asr_confidence, intent_confidence, pre_slots, channel, t_start
    ) -> dict:
        tel = _telemetry()
        tel.emit("WorkflowStarted", 1.0, {"scheme": scheme_name})

        # [4] Slot collection via workflow engine
        try:
            engine = _engine()
            if pre_slots:
                # Seed pre-collected slots into session
                from agentic_engine.storage import LocalJSONStorage
                from agentic_engine.session_manager import SessionManager
                import os
                session_file = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "agentic_engine", "sessions.json"
                )
                sm = SessionManager(LocalJSONStorage(session_file))
                for k, v in pre_slots.items():
                    sm.update_data(session_id, k, v)

            eng_result = engine(message=f"start_apply:{scheme_name}", session_id=session_id)
        except Exception as e:
            logger.error(f"[Supervisor] Slot agent error: {e}")
            return self._play_prompt(
                "एक समस्या हुई। कृपया पुनः प्रयास करें।",
                session_id, turn_id, "ERROR"
            )

        response_text  = eng_result.get("response", "")
        requires_input = eng_result.get("requires_input", True)
        is_terminal    = eng_result.get("is_terminal", False)

        # If still collecting slots, just return the next prompt
        if requires_input and not is_terminal:
            return self._build_response(
                session_id=session_id,
                turn_id=turn_id,
                intent="APPLY_SCHEME",
                response_text=response_text,
                language=language,
                requires_input=True,
                latency_ms=round((time.perf_counter() - t_start) * 1000, 2),
            )

        # [5] RULES AGENT — evaluate eligibility
        benefit_receipt = eng_result.get("benefit_receipt", {})
        rules_trace     = benefit_receipt.get("rules", [])
        rules_score     = float(benefit_receipt.get("confidence", 0.85))
        eligible        = benefit_receipt.get("eligible", False)

        # Audit eligibility
        case_id = f"JS-{__import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        try:
            _audit().log_eligibility(session_id, scheme_name, eligible, rules_score, rules_trace, case_id)
        except Exception:
            pass

        # [6] VERIFIER AGENT
        verifier_result = _verifier().assess(
            session_id=session_id,
            rules_score=rules_score,
            eligible=eligible,
            asr_confidence=asr_confidence,
            intent_confidence=intent_confidence,
        )
        decision   = verifier_result["decision"]
        risk_score = verifier_result["risk_score"]

        # [5b] Generate BenefitReceipt HTML
        receipt_data = {}
        try:
            from agentic_engine.storage import LocalJSONStorage
            from agentic_engine.session_manager import SessionManager
            import os as _os
            session_file = _os.path.join(
                _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
                "agentic_engine", "sessions.json"
            )
            sm   = SessionManager(LocalJSONStorage(session_file))
            sess = sm.get_session(session_id)
            slots_collected = {
                k: v for k, v in (sess.get("data", {}) if sess else {}).items()
                if not k.startswith("_")
            }

            receipt_data = _receipt().generate_receipt(
                session_id=session_id,
                scheme_name=scheme_name,
                eligible=eligible,
                rules_trace=rules_trace,
                rules_score=rules_score,
                slots=slots_collected,
                case_id=case_id,
                language=language,
            )
        except Exception as e:
            logger.warning(f"[Supervisor] Receipt generation failed: {e}")
            receipt_data = {"case_id": case_id, "eligible": eligible, "receipt_url": ""}

        receipt_url = receipt_data.get("receipt_url", "")

        # [7] WORKFLOW ORCHESTRATION AGENT
        wf_result = {}
        try:
            wf_result = _workflow().start_application_workflow(session_id, scheme_name)
        except Exception:
            pass

        # [8] NOTIFICATION AGENT + [9] HITL AGENT
        phone = pre_slots.get("mobile", "")

        if decision == "AUTO_SUBMIT":
            # Send submission SMS
            if phone:
                try:
                    _notify().notify_submission(phone, scheme_name, case_id)
                except Exception:
                    pass
            try:
                _audit().log_submission(session_id, case_id, scheme_name, "submitted")
            except Exception:
                pass
            tel.emit("SubmissionQueued", 1.0, {"scheme": scheme_name})
            tel.emit("WorkflowCompleted", 1.0, {"scheme": scheme_name})

            response_text = (
                f"✅ आप {receipt_data.get('scheme_name', scheme_name)} के लिए पात्र हैं! "
                f"Case ID: {case_id}। "
                f"आपको SMS में receipt link भेजा जायेगा।"
            )

        elif decision == "HITL_QUEUE":
            # Enqueue HITL
            try:
                _hitl().enqueue_case(
                    session_id=session_id,
                    turn_id=turn_id,
                    transcript=message,
                    response_text=response_text,
                    confidence=risk_score,
                    benefit_receipt=receipt_data,
                )
                _audit().log_hitl(session_id, case_id, "Verifier: risk score below auto-submit threshold")
            except Exception as e:
                logger.error(f"[Supervisor] HITL enqueue failed: {e}")
            if phone:
                try:
                    _notify().notify_hitl_queued(phone, scheme_name, case_id)
                except Exception:
                    pass
            response_text = (
                f"आपका आवेदन (Case ID: {case_id}) समीक्षा के लिए भेजा गया है। "
                "हमारी टीम 24 घंटे में आपसे संपर्क करेगी। SMS देखें।"
            )

        else:  # NOT_ELIGIBLE_NOTIFY
            if phone:
                try:
                    _notify().notify_rejected(phone, scheme_name, case_id)
                except Exception:
                    pass
            response_text = (
                f"❌ अभी के लिए आप {receipt_data.get('scheme_name', scheme_name)} के पात्र नहीं हैं। "
                "SMS में कारण और वैकल्पिक योजनाएं भेजी गई हैं। "
                "अधिक जानकारी के लिए अपने निकटतम CSC केंद्र जाएं।"
            )

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        return self._build_response(
            session_id=session_id,
            turn_id=turn_id,
            intent="APPLY_SCHEME",
            response_text=response_text,
            language=language,
            requires_input=False,
            latency_ms=latency_ms,
            benefit_receipt=receipt_data,
            verifier=verifier_result,
            case_id=case_id,
            receipt_url=receipt_url,
            workflow=wf_result,
        )

    # ── INFORMATION flow (agent 3) ────────────────────────────────────────────

    def _handle_information(self, session_id, turn_id, message, language, lang_det, t_start) -> dict:
        try:
            rag = _rag()
            # Try structured get_answer first (from rag_service.py)
            if hasattr(rag, "get_answer"):
                answer = rag.get_answer(message)
            elif hasattr(rag, "get_relevant_context"):
                ctx = rag.get_relevant_context(message)
                answer = ctx if isinstance(ctx, str) else str(ctx)
            else:
                answer = "I will send you information about that scheme via SMS."

            if not answer or len(answer.strip()) < 10:
                answer = "कृपया myscheme.gov.in या india.gov.in पर अधिक जानकारी लें।"

            # Truncate to 400 chars for IVR TTS
            if len(answer) > 400:
                answer = answer[:397] + "…"

            _telemetry().emit("WebChatQuery", 1.0, {"intent": "INFORMATION"})

        except Exception as e:
            logger.error(f"[Supervisor] RAG agent error: {e}")
            answer = "योजना की जानकारी: india.gov.in और myscheme.gov.in पर उपलब्ध है।"

        return self._build_response(
            session_id=session_id,
            turn_id=turn_id,
            intent="INFORMATION",
            response_text=answer,
            language=lang_det,
            requires_input=False,
            latency_ms=round((time.perf_counter() - t_start) * 1000, 2),
        )

    # ── STATUS flow ───────────────────────────────────────────────────────────

    def _handle_status(self, session_id, turn_id, language, t_start) -> dict:
        try:
            engine = _engine()
            result = engine(message="track_status", session_id=session_id)
            response_text = result.get("response", "आपके आवेदन की स्थिति SMS पर भेजी जायेगी।")
        except Exception:
            response_text = "आपके आवेदन की स्थिति एसएमएस पर भेजी जायेगी।"

        return self._build_response(
            session_id=session_id,
            turn_id=turn_id,
            intent="CHECK_STATUS",
            response_text=response_text,
            language=language,
            requires_input=False,
            latency_ms=round((time.perf_counter() - t_start) * 1000, 2),
        )

    # ── GRIEVANCE flow ────────────────────────────────────────────────────────

    def _handle_grievance(self, session_id, turn_id, message, language, t_start) -> dict:
        try:
            engine = _engine()
            result = engine(message=f"grievance:{message}", session_id=session_id)
            response_text = result.get("response", "आपकी शिकायत दर्ज कर ली गई है। SMS प्राप्त होगा।")
        except Exception:
            response_text = "आपकी शिकायत दर्ज हो गई। आपको SMS में जानकारी मिलेगी।"

        return self._build_response(
            session_id=session_id,
            turn_id=turn_id,
            intent="GRIEVANCE",
            response_text=response_text,
            language=language,
            requires_input=False,
            latency_ms=round((time.perf_counter() - t_start) * 1000, 2),
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _normalise_intent(self, intent: str) -> str:
        """Map any legacy/alias intent to agents.md canonical names."""
        mapping = {
            "apply":              "APPLY_SCHEME",
            "eligibility_check":  "APPLY_SCHEME",
            "info":               "INFORMATION",
            "scheme_lookup":      "INFORMATION",
            "document_required":  "INFORMATION",
            "general_query":      "INFORMATION",
            "track":              "CHECK_STATUS",
            "grievance":          "GRIEVANCE",
            "fallback":           "UNKNOWN",
        }
        return mapping.get(intent.lower(), intent.upper() if intent else "UNKNOWN")

    def _play_prompt(self, text: str, session_id: str, turn_id: str,
                     action: str, requires_input: bool = False) -> dict:
        """Return a minimal IVR/web prompt."""
        return self._build_response(
            session_id=session_id,
            turn_id=turn_id,
            intent=action,
            response_text=text,
            language="hi",
            requires_input=requires_input,
            latency_ms=0,
        )

    def _build_response(
        self,
        session_id: str,
        turn_id: str,
        intent: str,
        response_text: str,
        language: str,
        requires_input: bool,
        latency_ms: float = 0,
        benefit_receipt: Optional[dict] = None,
        verifier: Optional[dict] = None,
        case_id: Optional[str] = None,
        receipt_url: Optional[str] = None,
        workflow: Optional[dict] = None,
    ) -> dict:
        """Unified response shape for all channels."""
        # Best-effort Polly TTS
        audio_url = None
        try:
            from app.services.polly_service import PollyService
            audio_url = PollyService().synthesize(response_text, language)
        except Exception:
            pass

        return {
            "session_id":       session_id,
            "turn_id":          turn_id,
            "intent":           intent,
            "response_text":    response_text,
            "play_prompt":      response_text,     # alias for Connect webhook
            "audio_url":        audio_url,
            "language":         language,
            "requires_input":   requires_input,
            "case_id":          case_id,
            "receipt_url":      receipt_url,
            "benefit_receipt":  benefit_receipt or {},
            "verifier":         verifier or {},
            "workflow":         workflow or {},
            "debug": {
                "latency_ms":   latency_ms,
                "agent":        "JanSathiSupervisor",
                "pipeline":     "Telecom→Intent→Slot→Rules→Verifier→Workflow→Notify",
            }
        }


# ── Module-level singleton ────────────────────────────────────────────────────
_supervisor_instance: Optional[JanSathiSupervisor] = None

def get_supervisor() -> JanSathiSupervisor:
    global _supervisor_instance
    if _supervisor_instance is None:
        _supervisor_instance = JanSathiSupervisor()
    return _supervisor_instance


# ── Legacy shim (keeps existing agent/__init__.py happy) ─────────────────────
def execute_agent(request_data: dict) -> dict:
    """Backward-compat shim used by existing /agent/execute route."""
    return get_supervisor().orchestrate({
        "session_id": request_data.get("user_id", request_data.get("session_id", "")),
        "message":    request_data.get("message", ""),
        "language":   request_data.get("language", "hi"),
        "channel":    request_data.get("channel", "web"),
        "consent":    True,
    })
