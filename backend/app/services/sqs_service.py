"""
sqs_service.py — Amazon SQS HITL (Human-in-the-Loop) Queue
===========================================================
FIFO queue: jansathi-hitl.fifo
  - Used by hitl_service.enqueue_case() to send cases to SQS
  - Used by the admin worker Lambda to poll & process
  - Dead-letter queue: jansathi-hitl-dlq.fifo (after 3 retries)

Message envelope:
  { "case_id": "...", "session_id": "...", "scheme": "...",
    "confidence": 0.42, "context": {...}, "queued_at": "..." }
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

HITL_QUEUE_URL  = os.getenv("HITL_QUEUE_URL", "")
AWS_REGION      = os.getenv("AWS_REGION", "us-east-1")


class SQSService:
    """
    Wraps boto3 SQS operations for the HITL FIFO queue.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("sqs", region_name=AWS_REGION)
            except Exception as e:
                logger.warning(f"[SQS] boto3 unavailable: {e}")
        return self._client

    def _queue_url(self) -> str:
        """Return queue URL; raises if not configured."""
        url = HITL_QUEUE_URL
        if not url:
            raise RuntimeError(
                "HITL_QUEUE_URL env var is not set. "
                "Deploy messaging_stack first."
            )
        return url

    # ── Write ─────────────────────────────────────────────────────────────────

    def enqueue_hitl_case(
        self,
        case_id: str,
        session_id: str,
        user_id: str,
        scheme: str,
        confidence: float,
        context: dict,
        priority: str = "normal",   # "high" | "normal" | "low"
    ) -> bool:
        """
        Send a HITL case to SQS FIFO queue.
        MessageGroupId = scheme   (preserves order per scheme)
        MessageDeduplicationId = case_id (idempotent)
        """
        client = self._get_client()
        if not client:
            logger.info(f"[SQS] (local) enqueue_hitl_case case_id={case_id}")
            return True

        body = {
            "case_id":    case_id,
            "session_id": session_id,
            "user_id":    user_id,
            "scheme":     scheme,
            "confidence": confidence,
            "context":    context,
            "priority":   priority,
            "queued_at":  datetime.now(timezone.utc).isoformat(),
        }
        try:
            tag = f"high" if priority == "high" else "normal"
            resp = client.send_message(
                QueueUrl=self._queue_url(),
                MessageBody=json.dumps(body, default=str),
                MessageGroupId=f"{scheme}_{tag}",
                MessageDeduplicationId=case_id,
                MessageAttributes={
                    "Priority": {
                        "DataType": "String",
                        "StringValue": priority,
                    },
                },
            )
            mid = resp.get("MessageId", "?")
            logger.info(f"[SQS] Sent HITL case {case_id} → MessageId={mid}")
            return True
        except Exception as e:
            logger.error(f"[SQS] enqueue_hitl_case failed: {e}")
            return False

    def update_case_status(self, case_id: str, status: str,
                            resolution_notes: str = "") -> bool:
        """
        Send a status-update message to the same FIFO queue.
        Consumed by admin panel Lambda to update DynamoDB.
        """
        client = self._get_client()
        if not client:
            logger.info(f"[SQS] (local) update_case_status case_id={case_id} status={status}")
            return True

        body = {
            "message_type": "STATUS_UPDATE",
            "case_id":       case_id,
            "status":        status,
            "resolution_notes": resolution_notes,
            "updated_at":    datetime.now(timezone.utc).isoformat(),
        }
        try:
            resp = client.send_message(
                QueueUrl=self._queue_url(),
                MessageBody=json.dumps(body, default=str),
                MessageGroupId="status_updates",
                MessageDeduplicationId=f"{case_id}_status_{status}_{int(datetime.now().timestamp())}",
            )
            logger.info(f"[SQS] Status update {case_id} → {status} MessageId={resp.get('MessageId','?')}")
            return True
        except Exception as e:
            logger.error(f"[SQS] update_case_status failed: {e}")
            return False

    # ── Read (for admin worker Lambda) ────────────────────────────────────────

    def receive_messages(self, max_messages: int = 10,
                          wait_seconds: int = 20) -> list[dict]:
        """
        Long-poll for HITL cases from the queue.
        Returns list of {'receipt_handle': ..., 'body': {...}}.
        """
        client = self._get_client()
        if not client:
            return []

        try:
            resp = client.receive_message(
                QueueUrl=self._queue_url(),
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_seconds,
                MessageAttributeNames=["All"],
                AttributeNames=["All"],
            )
            messages = []
            for msg in resp.get("Messages", []):
                try:
                    body = json.loads(msg["Body"])
                except json.JSONDecodeError:
                    body = {"raw": msg["Body"]}
                messages.append({
                    "receipt_handle": msg["ReceiptHandle"],
                    "message_id":     msg["MessageId"],
                    "body":           body,
                    "attributes":     msg.get("MessageAttributes", {}),
                })
            return messages
        except Exception as e:
            logger.error(f"[SQS] receive_messages failed: {e}")
            return []

    def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a processed message from the queue using its receipt handle.
        Must be called after successful processing to prevent redelivery.
        """
        client = self._get_client()
        if not client:
            return True

        try:
            client.delete_message(
                QueueUrl=self._queue_url(),
                ReceiptHandle=receipt_handle,
            )
            return True
        except Exception as e:
            logger.error(f"[SQS] delete_message failed: {e}")
            return False

    def get_queue_attributes(self) -> dict:
        """Return current queue depth metrics (for health endpoint)."""
        client = self._get_client()
        if not client:
            return {}

        try:
            resp = client.get_queue_attributes(
                QueueUrl=self._queue_url(),
                AttributeNames=[
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                    "ApproximateNumberOfMessagesDelayed",
                ],
            )
            attrs = resp.get("Attributes", {})
            return {
                "visible":     int(attrs.get("ApproximateNumberOfMessages", 0)),
                "in_flight":   int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)),
                "delayed":     int(attrs.get("ApproximateNumberOfMessagesDelayed", 0)),
            }
        except Exception as e:
            logger.error(f"[SQS] get_queue_attributes failed: {e}")
            return {}
