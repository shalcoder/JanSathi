"""
whatsapp_adapter.py — Layer 1 Adapter for WhatsApp Messaging.
Transforms Twilio/Meta webhooks into the JanSathi UnifiedEventObject.
"""
from datetime import datetime
from app.automation.l1_integration.schema import UnifiedEventObject

class WhatsAppAdapter:
    @staticmethod
    def transform_twilio(form_data: dict) -> UnifiedEventObject:
        """
        Transforms Twilio WhatsApp POST data.
        """
        # Extract phone and session
        from_phone = form_data.get("From", "").replace("whatsapp:", "")
        message_body = form_data.get("Body", "")
        
        # Use phone as session_id for message continuity in dev
        session_id = f"wa-{from_phone}"
        
        return UnifiedEventObject(
            session_id=session_id,
            channel="whatsapp",
            language="hi", # Default to Hindi for now
            message=message_body,
            timestamp=datetime.utcnow(),
            channel_metadata={
                "phone": from_phone,
                "provider": "twilio",
                "wa_id": form_data.get("SmsMessageSid")
            }
        )

    @staticmethod
    def transform_meta(json_data: dict) -> UnifiedEventObject:
        """
        Transforms Meta (Cloud API) JSON payload.
        """
        # Basic placeholder for Meta Cloud API structure
        entry = json_data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        message = value.get("messages", [{}])[0]
        
        from_phone = message.get("from", "unknown")
        text = message.get("text", {}).get("body", "")
        
        return UnifiedEventObject(
            session_id=f"wa-{from_phone}",
            channel="whatsapp",
            message=text,
            channel_metadata={"phone": from_phone, "provider": "meta"}
        )
