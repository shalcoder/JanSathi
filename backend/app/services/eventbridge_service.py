"""
eventbridge_service.py — Amazon EventBridge Publisher
======================================================
Publishes structured domain events to the JanSathi event bus.
Other AWS services subscribe via EventBridge rules:
  - application_submitted  → Step Functions StartExecution
  - eligibility_checked    → CloudWatch metric + SNS alert
  - document_uploaded      → S3 trigger + Textract pipeline
  - hitl_case_created      → SQS HITL queue + admin notification
  - session_started        → CloudWatch analytics

Architecture:
  Lambda/Flask → EventBridge (jansathi-events bus) → Target rules
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

EVENT_BUS_NAME = os.getenv("EVENTBRIDGE_BUS_NAME", "jansathi-events")
EVENT_SOURCE    = "in.gov.jansathi"


class EventBridgeService:
    """
    Thin wrapper around boto3 EventBridge put_events.
    All JanSathi domain events flow through here.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    "events",
                    region_name=os.getenv("AWS_REGION", "us-east-1"),
                )
            except Exception as e:
                logger.warning(f"[EventBridge] boto3 unavailable: {e}")
        return self._client

    # ── Public event publishers ────────────────────────────────────────────────

    def publish(self, detail_type: str, detail: dict) -> bool:
        """
        Low-level publish. Returns True on success.
        detail_type: e.g. 'ApplicationSubmitted', 'EligibilityChecked'
        """
        client = self._get_client()
        if not client:
            logger.info(f"[EventBridge] (local) {detail_type}: {json.dumps(detail)[:120]}")
            return True   # graceful no-op in local dev

        entry = {
            "Source":       EVENT_SOURCE,
            "DetailType":   detail_type,
            "Detail":       json.dumps(detail, default=str),
            "EventBusName": EVENT_BUS_NAME,
            "Time":         datetime.now(timezone.utc),
        }
        try:
            resp = client.put_events(Entries=[entry])
            failed = resp.get("FailedEntryCount", 0)
            if failed:
                logger.error(f"[EventBridge] put_events failed: {resp['Entries']}")
                return False
            logger.info(f"[EventBridge] Published {detail_type} → {resp['Entries'][0].get('EventId','?')}")
            return True
        except Exception as e:
            logger.error(f"[EventBridge] publish error ({detail_type}): {e}")
            return False

    # ── Domain events ─────────────────────────────────────────────────────────

    def application_submitted(self, session_id: str, user_id: str, scheme: str,
                               case_id: str, eligible: bool, score: float,
                               slots: dict | None = None) -> bool:
        """
        Emitted after eligibility is confirmed and a benefit receipt is created.
        EventBridge rule → Step Functions StartExecution (ApplicationWorkflow).
        """
        return self.publish("ApplicationSubmitted", {
            "event_id":   str(uuid.uuid4()),
            "session_id": session_id,
            "user_id":    user_id,
            "scheme":     scheme,
            "case_id":    case_id,
            "eligible":   eligible,
            "score":      score,
            "slots":      slots or {},
        })

    def eligibility_checked(self, session_id: str, scheme: str,
                             eligible: bool, score: float, language: str) -> bool:
        """
        Emitted every time the rules engine finishes evaluation.
        EventBridge rule → CloudWatch custom metric + optional SNS admin alert if score < 0.5.
        """
        return self.publish("EligibilityChecked", {
            "event_id":   str(uuid.uuid4()),
            "session_id": session_id,
            "scheme":     scheme,
            "eligible":   eligible,
            "score":      score,
            "language":   language,
        })

    def document_uploaded(self, session_id: str, user_id: str,
                           doc_type: str, s3_key: str) -> bool:
        """
        Emitted when a citizen uploads a document.
        EventBridge rule → Textract async job trigger.
        """
        return self.publish("DocumentUploaded", {
            "event_id":   str(uuid.uuid4()),
            "session_id": session_id,
            "user_id":    user_id,
            "doc_type":   doc_type,
            "s3_key":     s3_key,
        })

    def hitl_case_created(self, case_id: str, session_id: str,
                           confidence: float, scheme: str) -> bool:
        """
        Emitted when a case is escalated to human review.
        EventBridge rule → SQS HITL queue + admin SNS alert.
        """
        return self.publish("HITLCaseCreated", {
            "event_id":   str(uuid.uuid4()),
            "case_id":    case_id,
            "session_id": session_id,
            "confidence": confidence,
            "scheme":     scheme,
        })

    def session_started(self, session_id: str, channel: str, language: str) -> bool:
        """
        Emitted at the start of every citizen interaction.
        EventBridge rule → CloudWatch usage analytics.
        """
        return self.publish("SessionStarted", {
            "event_id":   str(uuid.uuid4()),
            "session_id": session_id,
            "channel":    channel,
            "language":   language,
        })

    def voice_processed(self, session_id: str, language: str,
                         asr_job_id: str, duration_ms: int) -> bool:
        """Emitted after Transcribe completes. Triggers Polly TTS pipeline."""
        return self.publish("VoiceProcessed", {
            "event_id":     str(uuid.uuid4()),
            "session_id":   session_id,
            "language":     language,
            "asr_job_id":   asr_job_id,
            "duration_ms":  duration_ms,
        })
