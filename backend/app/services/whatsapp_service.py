"""
whatsapp_service.py — Thin stub (channel not in current JanSathi scope)

From agents.md scope:
  Voice → Eligibility → Checklist → SMS → Dashboard

WhatsApp is NOT a required channel in the current build.
This stub exists only for forward-compatibility.

For SMS notifications use notify_service.NotifyService (SNS).
If WhatsApp integration is added in future, wire it through
JanSathiSupervisor.orchestrate({"channel": "whatsapp", ...}).
"""

import logging
logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Out-of-scope stub. Forwards to NotifyService for SMS fallback.
    """

    def __init__(self):
        logger.info(
            "[WhatsAppService] WhatsApp channel is not in current scope. "
            "Using SNS SMS via notify_service for all outbound messages."
        )

    def process_incoming_message(self, message_data: dict) -> dict:
        """
        Not implemented. Returns structured event so caller can
        route through JanSathiSupervisor.
        """
        logger.warning("[WhatsAppService] process_incoming_message called — not wired.")
        return {
            "sender":  message_data.get("from", ""),
            "query":   message_data.get("text", {}).get("body", ""),
            "channel": "whatsapp",
            "status":  "not_implemented",
        }

    def send_scheme_info(self, to_number: str, scheme_data: dict) -> dict:
        """Stub: delegates to NotifyService SMS."""
        try:
            from app.services.notify_service import NotifyService
            ns = NotifyService()
            case_id = scheme_data.get("case_id", "N/A")
            scheme  = scheme_data.get("scheme_name", "Unknown Scheme")
            ns.notify_submission(to_number, scheme, case_id)
            return {"status": "delegated_to_sms", "to": to_number}
        except Exception as e:
            logger.error(f"[WhatsAppService] SMS fallback failed: {e}")
            return {"status": "failed", "to": to_number}
