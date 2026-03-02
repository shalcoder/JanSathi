"""
verification_tasks.py — Step Functions Lambda Handlers
Handles external verification steps (Aadhaar, Bank) in the JanSathi workflow.
"""
import json
import logging

logger = logging.getLogger(__name__)

def aadhaar_verify(event, context):
    """
    Simulates UIDAI Aadhaar verification.
    Event structure: { "id_number": "...", "name": "..." }
    """
    logger.info(f"Starting Aadhaar verification for: {event.get('id_number')}")
    
    # In production, this would call UIDAI Auth API via HTTPS/Signature
    # For JanSathi Prototype, we simulate success for registered test IDs
    id_num = event.get("id_number", "")
    
    if len(id_num) >= 12:
        return {
            "status": "verified",
            "auth_code": "UID-JANSATHI-OK",
            "message": "Aadhaar number verified successfully",
            "timestamp": "2026-03-02"
        }
    else:
        return {
            "status": "failed",
            "error_code": "INVALID_ID",
            "message": "Aadhaar number must be 12 digits"
        }

def bank_verify(event, context):
    """
    Simulates NPCI Direct Benefit Transfer (DBT) bank linking check.
    """
    logger.info(f"Checking bank linking for phone: {event.get('phone')}")
    
    # In production, this calls NPCI mapper
    return {
        "status": "active",
        "bank_name": "State Bank of India",
        "dbt_enabled": True,
        "last_updated": "2026-01-15"
    }
