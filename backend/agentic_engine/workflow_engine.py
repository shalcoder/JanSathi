import random
import string
from .state_machine import WorkflowState
from .session_manager import SessionManager

class AgenticWorkflowEngine:
    """
    Coordinates the workflow logic and session transitions.
    """
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def handle_input(self, session_id: str, user_input: str) -> dict:
        """
        Processes user input, updates session state, and returns a structured response.
        """
        user_input = user_input.strip()
        
        # Handle Restart logic
        if user_input.lower() == "restart":
            self.session_manager.create_session(session_id)  # Overwrites/Resets
            self.session_manager.update_state(session_id, WorkflowState.COLLECT_STATE)
            session = self.session_manager.get_session(session_id)
            return {
                "response": "Session restarted. Which state are you from?",
                "current_state": WorkflowState.COLLECT_STATE,
                "action_type": "ASK_STATE",
                "requires_input": True,
                "is_terminal": False,
                "session_data": session["data"]
            }

        session = self.session_manager.get_session(session_id)
        
        # If session does not exist, initialize it
        if not session:
            session = self.session_manager.create_session(session_id)
        
        current_state = session.get("current_state", WorkflowState.START)
        data = session.get("data", {})

        # 1. State: START
        if current_state == WorkflowState.START:
            next_state = WorkflowState.COLLECT_STATE
            self.session_manager.update_state(session_id, next_state)
            return {
                "response": "Which state are you from?",
                "current_state": next_state,
                "action_type": "ASK_STATE",
                "requires_input": True,
                "is_terminal": False,
                "session_data": self.session_manager.get_session(session_id)["data"]
            }

        # 2. State: COLLECT_STATE
        if current_state == WorkflowState.COLLECT_STATE:
            state_val = user_input.lower()
            self.session_manager.update_data(session_id, "state", state_val)
            next_state = WorkflowState.COLLECT_LAND_OWNERSHIP
            self.session_manager.update_state(session_id, next_state)
            return {
                "response": "Do you own farming land? (Yes/No)",
                "current_state": next_state,
                "action_type": "ASK_LAND_OWNERSHIP",
                "requires_input": True,
                "is_terminal": False,
                "session_data": self.session_manager.get_session(session_id)["data"]
            }

        # 3. State: COLLECT_LAND_OWNERSHIP
        if current_state == WorkflowState.COLLECT_LAND_OWNERSHIP:
            land_val = user_input.lower()
            self.session_manager.update_data(session_id, "land_owned", land_val)
            next_state = WorkflowState.EVALUATE_ELIGIBILITY
            self.session_manager.update_state(session_id, next_state)
            # Proceed to auto-evaluate
            return self.handle_input(session_id, "AUTO_EVALUATE")

        # 4. State: EVALUATE_ELIGIBILITY
        if current_state == WorkflowState.EVALUATE_ELIGIBILITY:
            state = data.get("state", "")
            land = data.get("land_owned", "")
            
            if state == "tamil nadu" and land == "yes":
                next_state = WorkflowState.ELIGIBLE
                self.session_manager.update_state(session_id, next_state)
                return {
                    "response": "Congratulations, you are eligible for PM-Kisan! Would you like to file a grievance to expedite your payment? (Yes/No)",
                    "current_state": next_state,
                    "action_type": "ELIGIBILITY_RESULT",
                    "requires_input": True,
                    "is_terminal": False,
                    "session_data": self.session_manager.get_session(session_id)["data"]
                }
            else:
                next_state = WorkflowState.NOT_ELIGIBLE
                self.session_manager.update_state(session_id, next_state)
                return {
                    "response": "Sorry, based on your inputs, you are not eligible for this scheme at this time.",
                    "current_state": next_state,
                    "action_type": "ELIGIBILITY_RESULT",
                    "requires_input": False,
                    "is_terminal": False,
                    "session_data": self.session_manager.get_session(session_id)["data"]
                }

        # 5. State: ELIGIBLE (Offer Grievance)
        if current_state == WorkflowState.ELIGIBLE:
            if user_input.lower() == "yes":
                next_state = WorkflowState.OFFER_GRIEVANCE
                self.session_manager.update_state(session_id, next_state)
                # Proceed to offer grievance
                return self.handle_input(session_id, "AUTO_OFFER")
            else:
                next_state = WorkflowState.COMPLETED
                self.session_manager.update_state(session_id, next_state)
                return {
                    "response": "Thank you for using JanSathi. Goodbye!",
                    "current_state": next_state,
                    "action_type": "SESSION_COMPLETED",
                    "requires_input": False,
                    "is_terminal": True,
                    "session_data": self.session_manager.get_session(session_id)["data"]
                }

        # 6. State: NOT_ELIGIBLE
        if current_state == WorkflowState.NOT_ELIGIBLE:
            next_state = WorkflowState.COMPLETED
            self.session_manager.update_state(session_id, next_state)
            return {
                "response": "Workflow completed. Thank you.",
                "current_state": next_state,
                "action_type": "SESSION_COMPLETED",
                "requires_input": False,
                "is_terminal": True,
                "session_data": self.session_manager.get_session(session_id)["data"]
            }

        # 7. State: OFFER_GRIEVANCE
        if current_state == WorkflowState.OFFER_GRIEVANCE:
            next_state = WorkflowState.DRAFT_GRIEVANCE
            self.session_manager.update_state(session_id, next_state)
            return {
                "response": "Drafting your grievance... Please confirm if the following text is okay: 'Farmer from {state} requesting PM-Kisan assistance.' (Confirm/Cancel)".format(state=data.get("state", "unknown")),
                "current_state": next_state,
                "action_type": "GRIEVANCE_DRAFTED",
                "requires_input": True,
                "is_terminal": False,
                "session_data": self.session_manager.get_session(session_id)["data"]
            }

        # 8. State: DRAFT_GRIEVANCE
        if current_state == WorkflowState.DRAFT_GRIEVANCE:
            if user_input.lower() in ["confirm", "yes"]:
                next_state = WorkflowState.SUBMIT_GRIEVANCE
                self.session_manager.update_state(session_id, next_state)
                # Proceed to submit
                return self.handle_input(session_id, "AUTO_SUBMIT")
            else:
                next_state = WorkflowState.COMPLETED
                self.session_manager.update_state(session_id, next_state)
                return {
                    "response": "Grievance cancelled. Goodbye!",
                    "current_state": next_state,
                    "action_type": "SESSION_COMPLETED",
                    "requires_input": False,
                    "is_terminal": True,
                    "session_data": self.session_manager.get_session(session_id)["data"]
                }

        # 9. State: SUBMIT_GRIEVANCE
        if current_state == WorkflowState.SUBMIT_GRIEVANCE:
            grievance_id = "GRV-" + "".join(random.choices(string.digits, k=6))
            self.session_manager.update_data(session_id, "grievance_id", grievance_id)
            next_state = WorkflowState.COMPLETED
            self.session_manager.update_state(session_id, next_state)
            return {
                "response": f"Your grievance has been submitted successfully. Your ID is {grievance_id}.",
                "current_state": next_state,
                "action_type": "GRIEVANCE_SUBMITTED",
                "requires_input": False,
                "is_terminal": True,
                "session_data": self.session_manager.get_session(session_id)["data"]
            }

        # 10. State: COMPLETED
        if current_state == WorkflowState.COMPLETED:
            return {
                "response": "Session already completed. Type 'restart' to begin again.",
                "current_state": WorkflowState.COMPLETED,
                "action_type": "SESSION_COMPLETED",
                "requires_input": False,
                "is_terminal": True,
                "session_data": self.session_manager.get_session(session_id)["data"]
            }

        # Default fallback
        return {
            "response": "I didn't understand that. Please try again.",
            "current_state": current_state,
            "action_type": "INVALID_STATE",
            "requires_input": True,
            "is_terminal": False,
            "session_data": self.session_manager.get_session(session_id)["data"]
        }
