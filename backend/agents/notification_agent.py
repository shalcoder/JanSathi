"""
notification_agent.py — Agent 8: SMS & Receipt Notifications
=============================================================
Responsibilities:
  - Send SMS via SNS (submission confirmation / HITL queue notice / rejection notice)
  - Store Benefit Receipt (logs it; S3 upload in production)
  - Set state["sms_sent"] = True

Always the final node before END.
"""
import os
import json
import logging
import sys

from .state import JanSathiState

logger = logging.getLogger(__name__)


def notification_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 8: Notification Agent.
    Sends SMS and logs/stores the Benefit Receipt.
    """
    session_id = state.get("session_id", "unknown")
    phone = state.get("phone", "")
    scheme_hint = state.get("scheme_hint", "unknown")
    decision = state.get("verifier_result", {}).get("decision", "NOT_ELIGIBLE_NOTIFY")
    benefit_receipt = state.get("benefit_receipt", {})
    hitl_case_id = state.get("hitl_case_id", "")
    intent = state.get("intent", "info")

    logger.info(f"[NotificationAgent] session={session_id} decision={decision} phone={'yes' if phone else 'no'}")

    sms_sent = False
    scheme_display = scheme_hint.replace("_", " ").title()
    case_id = benefit_receipt.get("receipt_id", session_id)

    # ── SMS Dispatch ──────────────────────────────────────────────────────────
    if phone:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from app.services.notify_service import NotifyService
            notify = NotifyService()

            if decision == "AUTO_SUBMIT" and intent == "apply":
                result = notify.notify_submission(phone, scheme_display, case_id)
            elif decision == "HITL_QUEUE":
                case_id = hitl_case_id or case_id
                result = notify.notify_hitl_queued(phone, scheme_display, case_id)
            else:
                # NOT_ELIGIBLE or info/grievance/track
                result = notify.notify_rejected(phone, scheme_display, case_id)

            sms_sent = result.get("success", False)
            logger.info(f"[NotificationAgent] SMS result: {result}")
        except Exception as e:
            logger.error(f"[NotificationAgent] SMS dispatch failed: {e}")
    else:
        logger.info(f"[NotificationAgent] No phone number, skipping SMS")

    # ── Store Benefit Receipt ─────────────────────────────────────────────────
    if benefit_receipt:
        _store_receipt(session_id, benefit_receipt)

    # ── Emit telemetry event ──────────────────────────────────────────────────
    _emit_telemetry(session_id, decision, sms_sent, scheme_hint)

    updated = dict(state)
    updated["sms_sent"] = sms_sent
    return updated


def _store_receipt(session_id: str, receipt: dict) -> None:
    """
    Store the Benefit Receipt.
    Production: upload to S3.
    Development: write to local agentic_engine/receipts/ folder.
    """
    s3_bucket = os.getenv("S3_RECEIPT_BUCKET", "")

    if s3_bucket:
        # Production: S3 upload
        try:
            import boto3
            region = os.getenv("AWS_REGION", "us-east-1")
            s3 = boto3.client("s3", region_name=region)
            key = f"receipts/{session_id}/{receipt.get('receipt_id', session_id)}.json"
            s3.put_object(
                Bucket=s3_bucket,
                Key=key,
                Body=json.dumps(receipt, indent=2, default=str),
                ContentType="application/json",
            )
            logger.info(f"[NotificationAgent] Receipt uploaded to s3://{s3_bucket}/{key}")
        except Exception as e:
            logger.error(f"[NotificationAgent] S3 upload failed: {e}")
    else:
        # Development: local file
        try:
            receipts_dir = os.path.join(
                os.path.dirname(__file__), "..", "agentic_engine", "receipts"
            )
            os.makedirs(receipts_dir, exist_ok=True)
            receipt_path = os.path.join(receipts_dir, f"{receipt.get('receipt_id', session_id)}.json")
            with open(receipt_path, "w", encoding="utf-8") as f:
                json.dump(receipt, f, indent=2, default=str)
            logger.info(f"[NotificationAgent] Receipt saved locally: {receipt_path}")
        except Exception as e:
            logger.error(f"[NotificationAgent] Local receipt save failed: {e}")


def _emit_telemetry(session_id: str, decision: str, sms_sent: bool, scheme: str) -> None:
    """Emit telemetry event for monitoring."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app.services.telemetry_service import get_telemetry
        t = get_telemetry()
        t.emit("AgentPipelineComplete", 1.0, {
            "session_id": session_id,
            "decision": decision,
            "scheme": scheme,
            "sms_sent": str(sms_sent),
        })
    except Exception:
        pass
