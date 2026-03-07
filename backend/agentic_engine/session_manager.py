from .state_machine import WorkflowState
from .storage import BaseSessionStorage
import time

class SessionManager:
    """
    Manages user sessions using a pluggable storage backend.
    """
    def __init__(self, storage: BaseSessionStorage):
        self.storage = storage
        self.storage.initialize()

    def create_session(self, session_id):
        """Creates a new session with initial state."""
        session_data = {
            "current_state": WorkflowState.START,
            "data": {},
            "created_at": time.time()
        }
        self.storage.put_session(session_id, session_data)
        return session_data

    def get_session(self, session_id):
        """Retrieves a session by ID."""
        return self.storage.get_session(session_id)

    def update_state(self, session_id, new_state):
        """
        Updates the state of a session after validating the transition.
        """
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")
        
        current_state = session["current_state"]
        # Convert string state to Choice if necessary
        if WorkflowState.is_valid_transition(current_state, new_state):
            session["current_state"] = new_state
            self.storage.put_session(session_id, session)
        else:
            raise ValueError(f"Invalid transition from {current_state} to {new_state}")

    def update_data(self, session_id, key, value):
        """Updates the data dictionary of a session."""
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")
        
        session["data"][key] = value
        self.storage.put_session(session_id, session)

    def list_all_sessions(self):
        """Legacy support for listing all sessions (only for local storage)."""
        try:
            return self.storage.load()
        except NotImplementedError:
            return {}
