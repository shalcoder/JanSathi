"""
hitl_service.py – Human-in-the-Loop ticket management.

Writes low-confidence cases to storage and provides
list / resolve operations used by the admin API.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Storage helpers – DynamoDB when configured, otherwise local JSON file
# ──────────────────────────────────────────────────────────────────────────────

HITL_LOCAL_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "agentic_engine", "hitl_cases.json"
)


def _load_local() -> dict:
    if not os.path.exists(HITL_LOCAL_FILE):
        return {}
    with open(HITL_LOCAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_local(data: dict) -> None:
    os.makedirs(os.path.dirname(HITL_LOCAL_FILE), exist_ok=True)
    with open(HITL_LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _get_dynamo_table():
    """Returns a DynamoDB Table resource or None if not configured."""
    try:
        import boto3
        table_name = os.getenv("HITL_TABLE", "JanSathiHITLCases")
        region = os.getenv("AWS_REGION", "us-east-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        return dynamodb.Table(table_name)
    except Exception as e:
        logger.warning(f"[HITLService] DynamoDB unavailable, using local storage: {e}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

class HITLService:
    """
    Manages the Human-in-the-Loop review queue.
    Supports both DynamoDB (production) and local JSON (development).
    """

    def enqueue_case(
        self,
        session_id: str,
        turn_id: str,
        transcript: str,
        response_text: str,
        confidence: float,
        benefit_receipt: Optional[dict] = None,
        audio_url: Optional[str] = None,
        slots: Optional[dict] = None,
    ) -> dict:
        """
        Write a new HITL review ticket.
        Returns the created case dict.
        """
        case_id = f"hitl-{uuid.uuid4().hex[:10]}"
        case = {
            "id": case_id,
            "session_id": session_id,
            "turn_id": turn_id,
            "transcript": transcript,
            "response_text": response_text,
            "confidence": confidence,
            "benefit_receipt": benefit_receipt or {},
            "audio_url": audio_url or "",
            "slots": slots or {},
            "status": "pending_review",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        table = _get_dynamo_table()
        if table:
            table.put_item(Item=case)
        else:
            store = _load_local()
            store[case_id] = case
            _save_local(store)

        logger.info(f"[HITLService] Enqueued case {case_id} (session={session_id}, conf={confidence:.2f})")
        return case

    def get_cases(self, status: str = "pending_review") -> list:
        """Return all HITL cases with the given status."""
        table = _get_dynamo_table()
        if table:
            try:
                from boto3.dynamodb.conditions import Attr
                response = table.scan(FilterExpression=Attr("status").eq(status))
                return response.get("Items", [])
            except Exception as e:
                logger.error(f"[HITLService] DynamoDB scan failed: {e}")
                return []
        else:
            store = _load_local()
            return [c for c in store.values() if c.get("status") == status]

    def resolve_case(self, case_id: str, action: str, reason: Optional[str] = None) -> dict:
        """
        Resolve a HITL case.
        action: 'approve' | 'reject'
        Returns updated case or error dict.
        """
        if action not in ("approve", "reject"):
            return {"error": f"Invalid action: {action}"}

        new_status = "approved" if action == "approve" else "rejected"
        now = datetime.now(timezone.utc).isoformat()

        table = _get_dynamo_table()
        if table:
            try:
                table.update_item(
                    Key={"id": case_id},
                    UpdateExpression="SET #s = :s, updated_at = :u, resolution_reason = :r",
                    ExpressionAttributeNames={"#s": "status"},
                    ExpressionAttributeValues={
                        ":s": new_status,
                        ":u": now,
                        ":r": reason or ""
                    }
                )
                return {"id": case_id, "status": new_status}
            except Exception as e:
                logger.error(f"[HITLService] DynamoDB update failed: {e}")
                return {"error": str(e)}
        else:
            store = _load_local()
            if case_id not in store:
                return {"error": "Case not found"}
            store[case_id]["status"] = new_status
            store[case_id]["updated_at"] = now
            store[case_id]["resolution_reason"] = reason or ""
            _save_local(store)
            return {"id": case_id, "status": new_status}

    def get_case(self, case_id: str) -> Optional[dict]:
        """Fetch a single case by ID."""
        table = _get_dynamo_table()
        if table:
            try:
                response = table.get_item(Key={"id": case_id})
                return response.get("Item")
            except Exception:
                return None
        else:
            return _load_local().get(case_id)
