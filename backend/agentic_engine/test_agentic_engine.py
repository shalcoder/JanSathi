import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_engine.storage import LocalJSONStorage, DynamoDBStorage
from agentic_engine.session_manager import SessionManager
from agentic_engine.workflow_engine import AgenticWorkflowEngine
from agentic_engine.state_machine import WorkflowState

def run_test():
    print("=== JanSathi Agentic Engine: Full Workflow Test ===")
    
    # Storage Selection
    storage_type = os.getenv("SESSION_STORAGE", "local").lower()
    session_file = os.path.join(os.path.dirname(__file__), "sessions.json")
    
    if storage_type == "local":
        if os.path.exists(session_file):
            os.remove(session_file)
        storage = LocalJSONStorage(session_file)
    elif storage_type == "dynamodb":
        storage = DynamoDBStorage(table_name="JanSathiSessions")
    else:
        raise ValueError(f"Unknown SESSION_STORAGE type: {storage_type}")

    print(f"[AgenticEngine] Using storage: {storage_type}")
    
    session_manager = SessionManager(storage)
    engine = AgenticWorkflowEngine(session_manager)
    session_id = "test_user_eligible"

    # Step 1: Start
    print("\n[Step 1] Initializing...")
    res = engine.handle_input(session_id, "hi")
    print(f"Agent: {res['response']}")

    # Step 2: Provide State
    print("\n[Step 2] User provides State...")
    res = engine.handle_input(session_id, "Tamil Nadu")
    print(f"Agent: {res['response']}")

    # Step 3: Provide Land Ownership
    print("\n[Step 3] User provides Land Ownership...")
    res = engine.handle_input(session_id, "Yes")
    print(f"Agent: {res['response']}")

    # Step 4: Offer Grievance
    print("\n[Step 4] User wants to file grievance...")
    res = engine.handle_input(session_id, "Yes")
    print(f"Agent: {res['response']}")

    # Step 5: Confirm Grievance
    print("\n[Step 5] User confirms grievance...")
    res = engine.handle_input(session_id, "Confirm")
    print(f"Agent: {res['response']}")

    # Step 6: Verify Completion
    print("\n[Step 6] Final check...")
    res = engine.handle_input(session_id, "hello?")
    print(f"Agent: {res['response']}")

    # Step 7: Test Restart
    print("\n[Step 7] Testing Restart...")
    res = engine.handle_input(session_id, "restart")
    print(f"Agent: {res['response']}")

    print("\n=== Test Completed Successfully ===")

if __name__ == "__main__":
    run_test()
