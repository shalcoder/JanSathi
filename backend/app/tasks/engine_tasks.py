"""
engine_tasks.py — Step Functions Lambda Handlers
Integrates the JanSathi Rules Engine and Receipt Service into the AWS workflow.
"""
import json
import logging
import os
from app.services.rules_engine import RulesEngine
from app.services.receipt_service import ReceiptService
from agentic_engine.session_manager import SessionManager
from agentic_engine.storage import LocalJSONStorage

logger = logging.getLogger(__name__)

def evaluate_eligibility(event, context):
    """
    Runs the deterministic RulesEngine against collected session data.
    Event structure: { "session_id": "...", "scheme_id": "..." }
    """
    session_id = event.get("session_id")
    scheme_id = event.get("scheme_id", "pm_kisan")
    
    # Initialize Engine
    engine = RulesEngine()
    
    # Load session data (using DynamoDB storage in production)
    # For Lambda, we assume env vars point to the right table
    from agentic_engine.storage import DynamoDBStorage
    storage = DynamoDBStorage(os.getenv("DYNAMODB_SESSIONS_TABLE", "JanSathi-Sessions"))
    data = storage.get_session_data(session_id)
    
    # Load scheme config (simulated for lambda)
    # In production, this would be in a shared S3/Config layer
    rules = {
        "mandatory": [
            {"field": "land_hectares", "operator": "lte", "value": 2.0, "label": "Land < 2ha"},
            {"field": "annual_income", "operator": "lte", "value": 200000, "label": "Income < 2L"}
        ]
    }
    
    eligible, breakdown, score = engine.evaluate(data, rules)
    
    return {
        "eligible": eligible,
        "score": score,
        "breakdown": breakdown,
        "session_id": session_id
    }

def generate_artifact(event, context):
    """
    Generates the HTML BenefitReceipt and uploads to S3.
    """
    session_id = event.get("session_id")
    receipt_service = ReceiptService()
    
    # Generate receipt using session results
    receipt_data = {
        "scheme_name": "PM-Kisan",
        "status": "Eligible" if event.get("eligible") else "Ineligible",
        "score": event.get("score"),
        "timestamp": "2026-03-02"
    }
    
    s3_url = receipt_service.generate_and_upload(session_id, receipt_data)
    
    return {
        "receipt_url": s3_url,
        "status": "generated",
        "session_id": session_id
    }
