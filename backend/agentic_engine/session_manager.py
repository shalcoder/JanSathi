from .state_machine import WorkflowState
from .storage import BaseSessionStorage

class SessionManager:
    """
    Manages user sessions using a pluggable storage backend.
    """
    def __init__(self, storage: BaseSessionStorage):
        self.storage = storage
        self.sessions = {}
        self.load_sessions()

    def load_sessions(self):
        """Loads sessions via the storage backend."""
        self.storage.initialize()
        self.sessions = self.storage.load()

    def save_sessions(self):
        """Saves current sessions via the storage backend."""
        self.storage.save(self.sessions)

    def create_session(self, session_id):
        """Creates a new session with initial state."""
        self.sessions[session_id] = {
            "current_state": WorkflowState.START,
            "data": {}
        }
        self.save_sessions()
        return self.sessions[session_id]

    def get_session(self, session_id):
        """Retrieves a session by ID."""
        return self.sessions.get(session_id)

    def update_state(self, session_id, new_state):
        """
        Updates the state of a session after validating the transition.
        """
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")
        
        current_state = session["current_state"]
        if WorkflowState.is_valid_transition(current_state, new_state):
            session["current_state"] = new_state
            self.save_sessions()
        else:
            raise ValueError(f"Invalid transition from {current_state} to {new_state}")

    def update_data(self, session_id, key, value):
        """Updates the data dictionary of a session."""
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")
        
        session["data"][key] = value
        self.save_sessions()
