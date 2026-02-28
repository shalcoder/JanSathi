class WorkflowState:
    """
    Defines the states and allowed transitions for the JanSathi Agentic Workflow.
    """
    START = "START"
    COLLECT_STATE = "COLLECT_STATE"
    COLLECT_LAND_OWNERSHIP = "COLLECT_LAND_OWNERSHIP"
    EVALUATE_ELIGIBILITY = "EVALUATE_ELIGIBILITY"
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    OFFER_GRIEVANCE = "OFFER_GRIEVANCE"
    DRAFT_GRIEVANCE = "DRAFT_GRIEVANCE"
    SUBMIT_GRIEVANCE = "SUBMIT_GRIEVANCE"
    COMPLETED = "COMPLETED"

    ALLOWED_TRANSITIONS = {
        START: [COLLECT_STATE],
        COLLECT_STATE: [COLLECT_LAND_OWNERSHIP],
        COLLECT_LAND_OWNERSHIP: [EVALUATE_ELIGIBILITY],
        EVALUATE_ELIGIBILITY: [ELIGIBLE, NOT_ELIGIBLE],
        ELIGIBLE: [OFFER_GRIEVANCE],
        NOT_ELIGIBLE: [COMPLETED],
        OFFER_GRIEVANCE: [DRAFT_GRIEVANCE, COMPLETED],
        DRAFT_GRIEVANCE: [SUBMIT_GRIEVANCE],
        SUBMIT_GRIEVANCE: [COMPLETED],
        COMPLETED: []
    }

    @staticmethod
    def is_valid_transition(current_state: str, next_state: str) -> bool:
        """
        Validates if transitioning from current_state to next_state is allowed.
        
        Args:
            current_state (str): The current state of the workflow.
            next_state (str): The proposed next state.
            
        Returns:
            bool: True if transition is allowed, False otherwise.
            
        Raises:
            ValueError: If current_state is not defined in ALLOWED_TRANSITIONS.
        """
        if current_state not in WorkflowState.ALLOWED_TRANSITIONS:
            raise ValueError(f"State '{current_state}' is not a valid workflow state.")
        
        return next_state in WorkflowState.ALLOWED_TRANSITIONS[current_state]
