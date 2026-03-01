"""
notify_service.py – SMS and receipt notifications.

Uses AWS SNS in production with a graceful console-log fallback
so the system keeps working during local development.
"""

import os
import uuid
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# SMS Templates
# ──────────────────────────────────────────────────────────────────────────────

SMS_TEMPLATES = {
    "submission": (
        "JanSathi: Your {scheme} application has been submitted. "
        "Case ID: {case_id}. "
        "View receipt: {receipt_url}"
    ),
    "hitl_queued": (
        "JanSathi: Your {scheme} application (Case ID: {case_id}) is under human review. "
        "We will notify you within 24 hours."
    ),
    "approved": (
        "JanSathi: Great news! Your {scheme} application (Case ID: {case_id}) has been APPROVED. "
        "Receipt: {receipt_url}"
    ),
    "rejected": (
        "JanSathi: Your {scheme} application (Case ID: {case_id}) could not be processed at this time. "
        "Please visit your nearest CSC center for assistance."
    ),
}


class NotifyService:
    """
    Handles SMS notifications via AWS SNS.
    Falls back to console logging if SNS is not configured.
    """

    def __init__(self):
        self.sns_client = None
        self.sender_id = os.getenv("SNS_SENDER_ID", "JanSathi")
        self.base_url = os.getenv("RECEIPT_BASE_URL", "https://jansathi.example.com/receipt")
        self._init_sns()

    def _init_sns(self):
        """Lazily initialise SNS client."""
        try:
            import boto3
            region = os.getenv("AWS_REGION", "ap-south-1")
            self.sns_client = boto3.client("sns", region_name=region)
            logger.info("[NotifyService] SNS client initialised")
        except Exception as e:
            logger.warning(f"[NotifyService] SNS unavailable, using console fallback: {e}")
            self.sns_client = None

    # ── Public API ────────────────────────────────────────────────────────────

    def send_sms(self, phone: str, message: str) -> dict:
        """
        Send an SMS via SNS Transactional.
        Returns {"success": True/False, "message_id": ...}
        """
        if not phone or not phone.strip():
            logger.warning("[NotifyService] No phone number provided, skipping SMS")
            return {"success": False, "reason": "no_phone"}

        # Ensure E.164 format for Indian numbers
        phone = self._normalise_phone(phone)

        if self.sns_client:
            try:
                response = self.sns_client.publish(
                    PhoneNumber=phone,
                    Message=message,
                    MessageAttributes={
                        "AWS.SNS.SMS.SMSType": {
                            "DataType": "String",
                            "StringValue": "Transactional"
                        },
                        "AWS.SNS.SMS.SenderID": {
                            "DataType": "String",
                            "StringValue": self.sender_id
                        }
                    }
                )
                msg_id = response.get("MessageId", "unknown")
                logger.info(f"[NotifyService] SMS sent to {phone[:6]}xxxx, MessageId={msg_id}")
                return {"success": True, "message_id": msg_id}
            except Exception as e:
                logger.error(f"[NotifyService] SNS publish failed: {e}")
                return {"success": False, "reason": str(e)}
        else:
            # Console fallback (dev/local mode)
            logger.info(f"[NotifyService][CONSOLE] SMS to {phone}: {message}")
            return {"success": True, "message_id": f"local-{uuid.uuid4().hex[:8]}"}

    def notify_submission(self, phone: str, scheme: str, case_id: str) -> dict:
        """Send submission confirmation SMS."""
        receipt_url = self.generate_benefit_receipt_url(case_id)
        msg = SMS_TEMPLATES["submission"].format(
            scheme=scheme, case_id=case_id, receipt_url=receipt_url
        )
        return self.send_sms(phone, msg)

    def notify_hitl_queued(self, phone: str, scheme: str, case_id: str) -> dict:
        """Notify user their case is under human review."""
        msg = SMS_TEMPLATES["hitl_queued"].format(scheme=scheme, case_id=case_id)
        return self.send_sms(phone, msg)

    def notify_approved(self, phone: str, scheme: str, case_id: str) -> dict:
        """Notify user their application was approved."""
        receipt_url = self.generate_benefit_receipt_url(case_id)
        msg = SMS_TEMPLATES["approved"].format(
            scheme=scheme, case_id=case_id, receipt_url=receipt_url
        )
        return self.send_sms(phone, msg)

    def notify_rejected(self, phone: str, scheme: str, case_id: str) -> dict:
        """Notify user their application was rejected."""
        msg = SMS_TEMPLATES["rejected"].format(scheme=scheme, case_id=case_id)
        return self.send_sms(phone, msg)

    def generate_benefit_receipt_url(self, case_id: str) -> str:
        """
        Generate a short URL linking to the Benefit Receipt.
        In production this would be an S3-hosted HTML page.
        """
        return f"{self.base_url}/{case_id}"

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _normalise_phone(self, phone: str) -> str:
        """Ensure E.164 format (+91XXXXXXXXXX for Indian numbers)."""
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "+91" + phone[1:]
        elif not phone.startswith("+"):
            phone = "+91" + phone
        return phone

    def log_event(self, session_id: str, event_type: str, data: dict = None) -> None:
        """
        Log a workflow terminal event (no phone required).
        Used by execution.py to record eligibility / grievance outcomes.
        Falls back to console in local mode.
        """
        payload = {
            "session_id": session_id,
            "event_type": event_type,
            "data": data or {},
        }
        logger.info(f"[NotifyService] Event logged: {payload}")
