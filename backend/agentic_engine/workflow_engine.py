import random
import string
import os
import logging
import yaml
from .state_machine import WorkflowState
from .session_manager import SessionManager

logger = logging.getLogger(__name__)

# Load schemes config once at module level
_SCHEMES_CONFIG: dict = {}


def _load_schemes():
    global _SCHEMES_CONFIG
    if _SCHEMES_CONFIG:
        return _SCHEMES_CONFIG
    try:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app", "data", "schemes_config.yaml"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            _SCHEMES_CONFIG = yaml.safe_load(f).get("schemes", {})
    except Exception as e:
        logger.warning(f"[WorkflowEngine] Could not load schemes_config.yaml: {e}")
        _SCHEMES_CONFIG = {}
    return _SCHEMES_CONFIG


class AgenticWorkflowEngine:
    """
    Coordinates the workflow logic and session transitions.

    Enhanced in v2:
      - Schema-driven multi-scheme slot collection (start_apply_workflow)
      - Deterministic eligibility via RulesEngine after all slots filled
      - HITL escalation when confidence < 0.8
      - Backward compat with PM-Kisan legacy path
    """

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        from app.services.rules_engine import RulesEngine
        self.rules_engine = RulesEngine()

    # ── Public entry point ─────────────────────────────────────────────────────

    def handle_input(self, session_id: str, user_input: str) -> dict:
        """
        Processes user input, updates session state, and returns a structured response.
        """
        user_input = user_input.strip()

        # Restart command
        if user_input.lower() == "restart":
            self.session_manager.create_session(session_id)
            self.session_manager.update_state(session_id, WorkflowState.COLLECT_STATE)
            return self._resp(session_id, "Session restarted. Which state are you from?", WorkflowState.COLLECT_STATE, "ASK_STATE", requires_input=True)

        # Start apply workflow command: "start_apply:<scheme>"
        if user_input.lower().startswith("start_apply:"):
            scheme_name = user_input.split(":", 1)[1].strip() or "pm_kisan"
            return self.start_apply_workflow(session_id, scheme_name)

        # Grievance command
        if user_input.lower().startswith("grievance:"):
            return self._handle_grievance(session_id, user_input[10:].strip())

        # Track status
        if user_input.lower() == "track_status":
            return self._handle_track(session_id)

        session = self.session_manager.get_session(session_id)
        if not session:
            session = self.session_manager.create_session(session_id)

        current_state = session.get("current_state", WorkflowState.START)
        data = session.get("data", {})

        # ── Schema-driven slot collection ──────────────────────────────────────
        if current_state == "COLLECT_SLOTS":
            return self._process_slot_answer(session_id, user_input)

        # ── Legacy PM-Kisan flow ───────────────────────────────────────────────
        if current_state == WorkflowState.START:
            self.session_manager.update_state(session_id, WorkflowState.COLLECT_STATE)
            return self._resp(session_id, "Which state are you from?", WorkflowState.COLLECT_STATE, "ASK_STATE", requires_input=True)

        if current_state == WorkflowState.COLLECT_STATE:
            self.session_manager.update_data(session_id, "state", user_input.lower())
            self.session_manager.update_state(session_id, WorkflowState.COLLECT_LAND_OWNERSHIP)
            return self._resp(session_id, "Do you own farming land? (Yes/No)", WorkflowState.COLLECT_LAND_OWNERSHIP, "ASK_LAND_OWNERSHIP", requires_input=True)

        if current_state == WorkflowState.COLLECT_LAND_OWNERSHIP:
            self.session_manager.update_data(session_id, "land_owned", user_input.lower())
            self.session_manager.update_state(session_id, WorkflowState.EVALUATE_ELIGIBILITY)
            return self.handle_input(session_id, "AUTO_EVALUATE")

        if current_state == WorkflowState.EVALUATE_ELIGIBILITY:
            return self._legacy_eligibility(session_id, data)

        if current_state == WorkflowState.ELIGIBLE:
            if user_input.lower() == "yes":
                self.session_manager.update_state(session_id, WorkflowState.OFFER_GRIEVANCE)
                return self.handle_input(session_id, "AUTO_OFFER")
            else:
                self.session_manager.update_state(session_id, WorkflowState.COMPLETED)
                return self._resp(session_id, "Thank you for using JanSathi. Goodbye!", WorkflowState.COMPLETED, "SESSION_COMPLETED", terminal=True)

        if current_state == WorkflowState.NOT_ELIGIBLE:
            self.session_manager.update_state(session_id, WorkflowState.COMPLETED)
            return self._resp(session_id, "Workflow completed. Thank you.", WorkflowState.COMPLETED, "SESSION_COMPLETED", terminal=True)

        if current_state == WorkflowState.OFFER_GRIEVANCE:
            state = data.get("state", "unknown")
            self.session_manager.update_state(session_id, WorkflowState.DRAFT_GRIEVANCE)
            return self._resp(session_id, f"Drafting grievance for farmer from {state}. Confirm? (Confirm/Cancel)", WorkflowState.DRAFT_GRIEVANCE, "GRIEVANCE_DRAFTED", requires_input=True)

        if current_state == WorkflowState.DRAFT_GRIEVANCE:
            if user_input.lower() in ["confirm", "yes"]:
                self.session_manager.update_state(session_id, WorkflowState.SUBMIT_GRIEVANCE)
                return self.handle_input(session_id, "AUTO_SUBMIT")
            else:
                self.session_manager.update_state(session_id, WorkflowState.COMPLETED)
                return self._resp(session_id, "Grievance cancelled. Goodbye!", WorkflowState.COMPLETED, "SESSION_COMPLETED", terminal=True)

        if current_state == WorkflowState.SUBMIT_GRIEVANCE:
            grievance_id = "GRV-" + "".join(random.choices(string.digits, k=6))
            self.session_manager.update_data(session_id, "grievance_id", grievance_id)
            self.session_manager.update_state(session_id, WorkflowState.COMPLETED)
            return self._resp(session_id, f"Your grievance has been submitted. ID: {grievance_id}.", WorkflowState.COMPLETED, "GRIEVANCE_SUBMITTED", terminal=True)

        if current_state == WorkflowState.COMPLETED:
            return self._resp(session_id, "Session completed. Type 'restart' to begin again.", WorkflowState.COMPLETED, "SESSION_COMPLETED", terminal=True)

        return self._resp(session_id, "I didn't understand that. Please try again.", current_state, "INVALID_STATE", requires_input=True)

    # ── Schema-driven apply workflow ───────────────────────────────────────────

    def start_apply_workflow(self, session_id: str, scheme_name: str) -> dict:
        """
        Start schema-driven slot collection for a given scheme.
        """
        schemes = _load_schemes()
        scheme = schemes.get(scheme_name)
        if not scheme:
            available = list(schemes.keys())
            return self._resp(
                session_id,
                f"I couldn't find scheme '{scheme_name}'. Available: {', '.join(available)}",
                "START", "SCHEME_NOT_FOUND", requires_input=True
            )

        slots = scheme.get("slots", [])
        session = self.session_manager.get_session(session_id) or self.session_manager.create_session(session_id)

        # Store slot metadata in session
        self.session_manager.update_data(session_id, "_scheme", scheme_name)
        self.session_manager.update_data(session_id, "_pending_slots", [s["key"] for s in slots])
        self.session_manager.update_data(session_id, "_slot_schemas", {s["key"]: s for s in slots})
        self.session_manager.update_state(session_id, "COLLECT_SLOTS")

        first_slot = slots[0]
        prompt = first_slot.get("prompt", f"Please provide your {first_slot['key']}")
        intro = f"I need a few details for {scheme.get('display_name', scheme_name)}.\n\n{prompt}"
        return self._resp(session_id, intro, "COLLECT_SLOTS", "COLLECTING_SLOTS", requires_input=True)

    def _process_slot_answer(self, session_id: str, user_input: str) -> dict:
        """Fill the current pending slot, move to next slot or evaluate eligibility."""
        session = self.session_manager.get_session(session_id)
        data = session.get("data", {})
        pending = list(data.get("_pending_slots", []))
        schemas: dict = data.get("_slot_schemas", {})
        scheme_name: str = data.get("_scheme", "pm_kisan")

        if not pending:
            return self._run_eligibility(session_id, scheme_name)

        current_key = pending[0]
        schema = schemas.get(current_key, {})

        # DTMF support
        value: any = user_input.strip()
        if value.startswith("DTMF:"):
            digit = value[5:]
            dtmf_map = schema.get("dtmf_map", {})
            value = dtmf_map.get(digit, digit)

        # Type coercion
        try:
            field_type = schema.get("type", "string")
            if field_type == "float":
                value = float(str(value).replace(",", ""))
            elif field_type == "int":
                value = int(value)
            elif field_type == "boolean":
                value = str(value).lower() in ("yes", "1", "true", "हाँ", "ஆம்")
        except (ValueError, TypeError):
            pass

        self.session_manager.update_data(session_id, current_key, value)
        pending.pop(0)
        self.session_manager.update_data(session_id, "_pending_slots", pending)

        if not pending:
            return self._run_eligibility(session_id, scheme_name)

        next_key = pending[0]
        next_schema = schemas.get(next_key, {})
        prompt = next_schema.get("prompt", f"Please provide your {next_key}")
        return self._resp(session_id, prompt, "COLLECT_SLOTS", "COLLECTING_SLOTS", requires_input=True)

    def _run_eligibility(self, session_id: str, scheme_name: str) -> dict:
        """Run RulesEngine against collected data and produce BenefitReceipt."""
        schemes = _load_schemes()
        scheme = schemes.get(scheme_name, {})
        rules = scheme.get("rules", {})
        sources = scheme.get("sources", [])

        session = self.session_manager.get_session(session_id)
        user_profile = {k: v for k, v in session.get("data", {}).items() if not k.startswith("_")}

        eligible, breakdown, score = self.rules_engine.evaluate(user_profile, rules)

        benefit_receipt = {
            "eligible": eligible,
            "scheme_name": scheme.get("display_name", scheme_name),
            "rules": breakdown,
            "sources": sources,
            "confidence": score,
        }

        self.session_manager.update_data(session_id, "benefit_receipt", benefit_receipt)
        self.session_manager.update_data(session_id, "eligibility_score", score)

        # Trigger HITL if confidence below threshold
        if score < 0.8:
            self._enqueue_hitl(session_id, scheme_name, benefit_receipt, score)
            self.session_manager.update_state(session_id, "HITL_PENDING")
            return self._resp(
                session_id,
                "Your application requires manual review. Our team will contact you within 24 hours. You will receive an SMS shortly.",
                "HITL_PENDING", "HITL_QUEUED", terminal=True,
                extra={"benefit_receipt": benefit_receipt}
            )

        if eligible:
            self.session_manager.update_state(session_id, WorkflowState.COMPLETED)
            resp_text = (
                f"✅ You are eligible for {scheme.get('display_name', scheme_name)}!\n"
                "Would you like to submit your application? (Yes/No)"
            )
            return self._resp(session_id, resp_text, "ELIGIBLE_CONFIRMED", "ELIGIBILITY_RESULT",
                              requires_input=True, extra={"benefit_receipt": benefit_receipt})
        else:
            self.session_manager.update_state(session_id, WorkflowState.COMPLETED)
            return self._resp(
                session_id,
                f"❌ Based on your inputs, you may not be eligible for {scheme.get('display_name', scheme_name)}. "
                "Please visit your nearest CSC for alternative schemes.",
                WorkflowState.COMPLETED, "ELIGIBILITY_RESULT", terminal=True,
                extra={"benefit_receipt": benefit_receipt}
            )

    # ── Grievance & Track handlers ─────────────────────────────────────────────

    def _handle_grievance(self, session_id: str, text: str) -> dict:
        grievance_id = "GRV-" + "".join(random.choices(string.digits, k=6))
        self.session_manager.get_session(session_id) or self.session_manager.create_session(session_id)
        self.session_manager.update_data(session_id, "grievance_id", grievance_id)
        self.session_manager.update_state(session_id, WorkflowState.COMPLETED)
        return self._resp(
            session_id,
            f"Your grievance has been registered. ID: {grievance_id}. You will receive an SMS confirmation.",
            WorkflowState.COMPLETED, "GRIEVANCE_SUBMITTED", terminal=True
        )

    def _handle_track(self, session_id: str) -> dict:
        session = self.session_manager.get_session(session_id)
        if not session:
            return self._resp(session_id, "No active session found. Please start a new conversation.", "START", "TRACK_NOT_FOUND", requires_input=False)
        data = session.get("data", {})
        grievance_id = data.get("grievance_id", "")
        benefit_receipt = data.get("benefit_receipt", {})
        if grievance_id:
            return self._resp(session_id, f"Your grievance {grievance_id} is under review. We will notify you via SMS.", session.get("current_state", "COMPLETED"), "TRACK_STATUS")
        if benefit_receipt:
            return self._resp(session_id, f"Application for {benefit_receipt.get('scheme_name', 'scheme')} — Status: Submitted. You will receive an SMS update.", session.get("current_state"), "TRACK_STATUS")
        return self._resp(session_id, "No active application found for tracking. Start with 'apply' first.", "START", "TRACK_NOT_FOUND")

    # ── Legacy eligibility ─────────────────────────────────────────────────────

    def _legacy_eligibility(self, session_id: str, data: dict) -> dict:
        state = data.get("state", "")
        land = data.get("land_owned", "")
        if state == "tamil nadu" and land == "yes":
            self.session_manager.update_state(session_id, WorkflowState.ELIGIBLE)
            return self._resp(session_id, "Congratulations, you are eligible for PM-Kisan! Would you like to file a grievance to expedite your payment? (Yes/No)", WorkflowState.ELIGIBLE, "ELIGIBILITY_RESULT", requires_input=True)
        else:
            self.session_manager.update_state(session_id, WorkflowState.NOT_ELIGIBLE)
            return self._resp(session_id, "Sorry, based on your inputs, you are not eligible for this scheme at this time.", WorkflowState.NOT_ELIGIBLE, "ELIGIBILITY_RESULT")

    # ── HITL enqueue ───────────────────────────────────────────────────────────

    def _enqueue_hitl(self, session_id: str, scheme_name: str, benefit_receipt: dict, confidence: float):
        try:
            from app.services.hitl_service import HITLService
            hitl = HITLService()
            session = self.session_manager.get_session(session_id)
            data = session.get("data", {}) if session else {}
            slots = {k: v for k, v in data.items() if not k.startswith("_")}
            hitl.enqueue_case(
                session_id=session_id,
                turn_id="auto",
                transcript=str(slots),
                response_text=f"Eligibility check for {scheme_name}: score={confidence:.2f}",
                confidence=confidence,
                benefit_receipt=benefit_receipt,
                slots=slots,
            )
        except Exception as e:
            logger.error(f"[WorkflowEngine] HITL enqueue failed: {e}")

    # ── Response builder ───────────────────────────────────────────────────────

    def _resp(self, session_id: str, response: str, current_state, action_type: str,
              requires_input: bool = False, terminal: bool = False, extra: dict = None) -> dict:
        session = self.session_manager.get_session(session_id)
        base = {
            "response": response,
            "current_state": current_state,
            "action_type": action_type,
            "requires_input": requires_input,
            "is_terminal": terminal,
            "session_data": session["data"] if session else {},
        }
        if extra:
            base.update(extra)
        return base
