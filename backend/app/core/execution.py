import os
import json
import logging
from typing import Dict

# Import Agentic Engine components
from agentic_engine.storage import LocalJSONStorage, DynamoDBStorage
from agentic_engine.session_manager import SessionManager
from agentic_engine.workflow_engine import AgenticWorkflowEngine

# Configure Logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ============================================================
# ENGINE INITIALIZATION (Singleton-like)
# ============================================================

# Global engine instance and initialization error
_engine = None
_init_error = None

def initialize_engine():
    """
    Initializes the storage, session manager, and workflow engine 
    based on environment variables.
    """
    global _engine, _init_error
    
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    try:
        if storage_type == "local":
            # Store sessions in the agentic_engine directory by default
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            session_file = os.path.join(base_dir, "agentic_engine", "sessions.json")
            logger.info(f"[Execution] Initializing LocalJSONStorage at {session_file}")
            storage = LocalJSONStorage(session_file)
        elif storage_type == "dynamodb":
            table_name = os.getenv("DYNAMODB_TABLE", "JanSathiSessions")
            region = os.getenv("AWS_REGION", "us-east-1")
            logger.info(f"[Execution] Initializing DynamoDBStorage (Table: {table_name}) (Region: {region})")
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

# Initial initialization
initialize_engine()

# ============================================================
# PURE INTERFACE FUNCTION
# ============================================================

def process_user_input(message: str, session_id: str) -> dict:
    """
    Primary entry point for any transport layer (IVR, Web, WhatsApp).
    
    Accepts:
        message (str): The raw text input from the user.
        session_id (str): Unique identifier for the user session.
        
    Returns:
        dict: Structured event response or error dictionary.
    """
    # 1. Validation
    if not session_id or not isinstance(session_id, str):
        return {
            "error": "Invalid session_id",
            "action_type": "ERROR",
            "response": "Internal System Error: Session ID missing."
        }
    
    if message is None:
        message = "" # Handle nulls gracefully
        
    # 2. Engine Availability Check
    if _engine is None:
        # Attempt re-initialization if it failed before (useful for transient env issues)
        initialize_engine()
        
    if _engine is None:
        return {
            "error": "Engine Not Initialized",
            "details": _init_error,
            "action_type": "ERROR",
            "response": f"Internal System Error: {_init_error or 'Agentic Engine is offline.'}"
        }
        
    # 3. Execution
    try:
        logger.info(f"[Execution] Processing input for Session: {session_id}")
        result = _engine.handle_input(session_id=session_id, user_input=str(message))
        return result
        
    except Exception as e:
        logger.error(f"[Execution] Runtime Error for Session {session_id}: {str(e)}")
        return {
            "error": str(type(e).__name__),
            "details": str(e),
            "action_type": "ERROR",
            "response": "I apologize, but I encountered an error processing your request. Please try again later."
        }
