"""
verification_tasks.py — Step Functions: Aadhaar & Bank Verification Lambdas
============================================================================
Each function is an independent Lambda handler invoked by Step Functions
as a task state. Input/output conform to the state machine definition in
infrastructure/stacks/workflow_stack.py.

State machine input (forwarded from EventBridge ApplicationSubmitted event):
  {
    "case_id":    "uuid",
    "session_id": "uuid",
    "user_id":    "string",
    "scheme":     "PM-KISAN",
    "slots": {
      "aadhaar_number": "XXXX-XXXX-XXXX",
      "bank_account":   "...",
      "ifsc_code":      "...",
    }
  }
"""

import os
import json
import logging
import boto3
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

HITL_TABLE = os.getenv("HITL_TABLE", "JanSathi-HITL-Cases")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


# ── Aadhaar Verification ──────────────────────────────────────────────────────

def aadhaar_verify(event: dict, context: Any) -> dict:
    """
    Lambda Task: Verify Aadhaar number via Verhoeff checksum (stub → UIDAI in prod).
    Returns updated state dict with aadhaar_status and aadhaar_name fields.
    """
    logger.info(f"[AadhaarVerify] case_id={event.get('case_id')}")

    aadhaar_number = event.get("slots", {}).get("aadhaar_number", "")
    # Legacy field support
    if not aadhaar_number:
        aadhaar_number = event.get("id_number", "")
    case_id = event.get("case_id", "")

    if not aadhaar_number:
        return {**event, "aadhaar_status": "SKIPPED", "aadhaar_name": ""}

    aadhaar_clean = aadhaar_number.replace("-", "").replace(" ", "")

    if not _is_valid_aadhaar(aadhaar_clean):
        _record_verification(case_id, "aadhaar", "FAILED", "Invalid format")
        return {
            **event,
            "aadhaar_status": "FAILED",
            "aadhaar_error":  "Invalid Aadhaar number format or checksum",
        }

    # Production: POST https://stage1.uidai.gov.in/onlineaadhaarverification/
    # with client cert + OTP (Aadhaar Auth API v2.5).
    # Hackathon stub: Verhoeff pass → VERIFIED
    result = {"status": "VERIFIED", "name": "Citizen"}
    _record_verification(case_id, "aadhaar", result["status"], "")

    return {
        **event,
        "aadhaar_status": result["status"],
        "aadhaar_name":   result["name"],
        "auth_code":      "UID-JANSATHI-OK",
        "verified_at":    datetime.now(timezone.utc).isoformat(),
    }


def bank_verify(event: dict, context: Any) -> dict:
    """
    Lambda Task: Verify bank account via NPCI / penny-drop.
    Only runs if aadhaar_status == 'VERIFIED'.
    """
    logger.info(f"[BankVerify] case_id={event.get('case_id')}")

    if event.get("aadhaar_status") not in ("VERIFIED", None):
        # Short-circuit if Aadhaar already failed
        return {**event, "bank_status": "SKIPPED"}

    slots   = event.get("slots", {})
    account = slots.get("bank_account", "")
    ifsc    = slots.get("ifsc_code", "")
    case_id = event.get("case_id", "")

    if not account or not ifsc:
        return {**event, "bank_status": "SKIPPED", "bank_error": "Missing bank details"}

    if not _is_valid_ifsc(ifsc):
        _record_verification(case_id, "bank", "FAILED", f"Invalid IFSC: {ifsc}")
        return {
            **event,
            "bank_status": "FAILED",
            "bank_error":  f"Invalid IFSC code: {ifsc}",
        }

    # Production: RazorpayX /v1/fund_accounts/validations or NPCI NACH API.
    # Hackathon stub: treat well-formed account+IFSC as VERIFIED.
    result = {
        "status":  "VERIFIED",
        "details": {
            "account":    account[-4:].rjust(len(account), "*"),
            "ifsc":       ifsc,
            "bank_name":  "State Bank of India",
            "dbt_enabled": True,
        },
    }
    _record_verification(case_id, "bank", result["status"], "")

    return {
        **event,
        "bank_status":  result["status"],
        "bank_details": result["details"],
        "verified_at":  datetime.now(timezone.utc).isoformat(),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_valid_aadhaar(number: str) -> bool:
    """Verhoeff algorithm checksum validation for 12-digit Aadhaar."""
    if len(number) != 12 or not number.isdigit():
        return False
    d = [
        [0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],
        [3,4,0,1,2,8,9,5,6,7],[4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],
        [6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],[8,7,6,5,9,3,2,1,0,4],
        [9,8,7,6,5,4,3,2,1,0],
    ]
    p = [
        [0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],
        [8,9,1,6,0,4,3,5,2,7],[9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],
        [2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8],
    ]
    c = 0
    for i, digit in enumerate(reversed(number)):
        c = d[c][p[i % 8][int(digit)]]
    return c == 0


def _is_valid_ifsc(ifsc: str) -> bool:
    import re
    return bool(re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc.upper()))


def _record_verification(case_id: str, kind: str, status: str, error: str) -> None:
    """Persist verification audit to DynamoDB HITL table."""
    if not case_id:
        return
    try:
        ddb   = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = ddb.Table(HITL_TABLE)
        table.update_item(
            Key={"case_id": case_id},
            UpdateExpression="SET verifications.#k = :v",
            ExpressionAttributeNames={"#k": kind},
            ExpressionAttributeValues={
                ":v": {
                    "status":     status,
                    "error":      error,
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }
            },
        )
    except Exception as e:
        logger.warning(f"[VerifyAudit] DynamoDB write failed: {e}")
