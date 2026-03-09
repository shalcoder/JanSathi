"""
hitl_service.py – Human-in-the-Loop ticket management.

Write path:  DynamoDB → SQS FIFO → EventBridge
Read path:   DynamoDB (or local JSON in dev)
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

HITL_LOCAL_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "agentic_engine", "hitl_cases.json"
)
HITL_TABLE = os.getenv("HITL_TABLE", "JanSathi-HITL-Cases")
AWS_REGION  = os.getenv("AWS_REGION", "us-east-1")


# ── Storage helpers ────────────────────────────────────────────────────────────

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
    try:
        import boto3
        ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
        return ddb.Table(HITL_TABLE)
    except Exception as e:
        logger.warning(f"[HITLService] DynamoDB unavailable: {e}")
        return None


# ── Public service class ───────────────────────────────────────────────────────

class HITLService:
    """
    Manages the Human-in-the-Loop review queue.
    Write path: DynamoDB → SQS FIFO → EventBridge (fire-and-forget, non-blocking).
    Read path:  DynamoDB (dev: local JSON fallback).
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
        scheme: str = "",
        user_id: str = "",
    ) -> dict:
        """
        Write a new HITL review ticket to DynamoDB, then fan out to SQS + EventBridge.
        """
        case_id    = f"hitl-{uuid.uuid4().hex[:10]}"
        created_at = datetime.now(timezone.utc).isoformat()
        case = {
            "case_id":        case_id,
            "id":             case_id,       # legacy alias
            "session_id":     session_id,
            "user_id":        user_id,
            "turn_id":        turn_id,
            "transcript":     transcript,
            "response_text":  response_text,
            "confidence":     str(confidence),
            "scheme":         scheme,
            "benefit_receipt": benefit_receipt or {},
            "audio_url":      audio_url or "",
            "slots":          slots or {},
            "status":         "pending_review",
            "created_at":     created_at,
            "updated_at":     created_at,
            "verifications":  {},
        }

        # 1 — DynamoDB (primary store)
        table = _get_dynamo_table()
        if table:
            table.put_item(Item=case)
        else:
            store = _load_local()
            store[case_id] = case
            _save_local(store)

        # 2 — SQS FIFO (async HITL worker pickup)
        try:
            from app.services.sqs_service import SQSService
            SQSService().enqueue_hitl_case(
                case_id=case_id,
                session_id=session_id,
                user_id=user_id,
                scheme=scheme,
                confidence=confidence,
                context={"transcript": transcript, "slots": slots or {}},
                priority="high" if confidence < 0.3 else "normal",
            )
        except Exception as e:
            logger.warning(f"[HITLService] SQS enqueue failed (non-fatal): {e}")

        # 3 — EventBridge (triggers admin alerts + CloudWatch)
        try:
            from app.services.eventbridge_service import EventBridgeService
            EventBridgeService().hitl_case_created(
                case_id=case_id,
                session_id=session_id,
                confidence=confidence,
                scheme=scheme,
            )
        except Exception as e:
            logger.warning(f"[HITLService] EventBridge publish failed (non-fatal): {e}")

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
        Resolve a HITL case. action: 'approve' | 'reject'
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
                    Key={"case_id": case_id, "created_at": self._get_created_at(case_id) or now},
                    UpdateExpression="SET #s = :s, updated_at = :u, resolution_reason = :r",
                    ExpressionAttributeNames={"#s": "status"},
                    ExpressionAttributeValues={
                        ":s": new_status,
                        ":u": now,
                        ":r": reason or "",
                    },
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
                # Scan by case_id (PK); we don't know created_at for get_item
                from boto3.dynamodb.conditions import Attr
                resp = table.scan(FilterExpression=Attr("case_id").eq(case_id))
                items = resp.get("Items", [])
                return items[0] if items else None
            except Exception:
                return None
        else:
            return _load_local().get(case_id)

    def _get_created_at(self, case_id: str) -> Optional[str]:
        """Retrieve created_at sort key for update_item."""
        case = self.get_case(case_id)
        return case.get("created_at") if case else None
