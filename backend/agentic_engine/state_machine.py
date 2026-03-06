class WorkflowState:
    """
    Defines the states and allowed transitions for the JanSathi Agentic Workflow.
    Includes both legacy PM-Kisan states and schema-driven multi-scheme states.
    """
    START = "START"

    # ── Legacy PM-Kisan states ────────────────────────────────────────────────
    COLLECT_STATE = "COLLECT_STATE"
    COLLECT_LAND_OWNERSHIP = "COLLECT_LAND_OWNERSHIP"
    EVALUATE_ELIGIBILITY = "EVALUATE_ELIGIBILITY"
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    OFFER_GRIEVANCE = "OFFER_GRIEVANCE"
    DRAFT_GRIEVANCE = "DRAFT_GRIEVANCE"
    SUBMIT_GRIEVANCE = "SUBMIT_GRIEVANCE"
    COMPLETED = "COMPLETED"

    # ── Schema-driven multi-scheme states ────────────────────────────────────
    COLLECT_SLOTS = "COLLECT_SLOTS"           # Generic slot collection (pm_awas, e_shram, etc.)
    ELIGIBILITY_RESULT = "ELIGIBILITY_RESULT" # After rules engine fires
    ELIGIBLE_CONFIRMED = "ELIGIBLE_CONFIRMED" # Eligibility confirmed — receipt generated
    HITL_PENDING = "HITL_PENDING"             # Human-in-the-loop review queue
    GRIEVANCE_SUBMITTED = "GRIEVANCE_SUBMITTED"

    ALLOWED_TRANSITIONS = {
        START: [COLLECT_STATE, COLLECT_SLOTS],

        # Legacy flow
        COLLECT_STATE: [COLLECT_LAND_OWNERSHIP, COLLECT_SLOTS],
        COLLECT_LAND_OWNERSHIP: [EVALUATE_ELIGIBILITY],
        EVALUATE_ELIGIBILITY: [ELIGIBLE, NOT_ELIGIBLE, ELIGIBILITY_RESULT, HITL_PENDING],
        ELIGIBLE: [OFFER_GRIEVANCE, ELIGIBLE_CONFIRMED, COMPLETED],
        NOT_ELIGIBLE: [COMPLETED, OFFER_GRIEVANCE],
        OFFER_GRIEVANCE: [DRAFT_GRIEVANCE, COMPLETED],
        DRAFT_GRIEVANCE: [SUBMIT_GRIEVANCE, COMPLETED],
        SUBMIT_GRIEVANCE: [COMPLETED, GRIEVANCE_SUBMITTED],
        COMPLETED: [],

        # Schema-driven flow
        COLLECT_SLOTS: [COLLECT_SLOTS, ELIGIBILITY_RESULT, HITL_PENDING, COMPLETED],
        ELIGIBILITY_RESULT: [ELIGIBLE_CONFIRMED, COMPLETED, HITL_PENDING],
        ELIGIBLE_CONFIRMED: [COMPLETED],
        HITL_PENDING: [ELIGIBLE_CONFIRMED, NOT_ELIGIBLE, COMPLETED],
        GRIEVANCE_SUBMITTED: [COMPLETED],
    }

    @staticmethod
    def is_valid_transition(current_state: str, next_state: str) -> bool:
        """
        Validates if transitioning from current_state to next_state is allowed.
        Returns True if valid, False otherwise.
        Does NOT raise — unknown states are treated as permissive (return True)
        so that schema-driven dynamic states don't crash the engine.
        """
        allowed = WorkflowState.ALLOWED_TRANSITIONS.get(current_state)
        if allowed is None:
            # Unknown state — permissive for forward compatibility
            return True
        return next_state in allowed
