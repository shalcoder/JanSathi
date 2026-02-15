from app.core.utils import logger
import os
import requests

class WhatsAppService:
    """
    Handling Multi-Modal WhatsApp interactions via Meta/Twilio Business API.
    Supports text queries, document uploads, and location-sharing.
    """
    def __init__(self):
        self.api_key = os.getenv("WHATSAPP_API_KEY")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_ID")

    def process_incoming_message(self, message_data):
        """
        Extracts intent from WhatsApp payload.
        Handles text, images (for OCR), and location.
        """
        sender = message_data.get('from')
        text = message_data.get('text', {}).get('body', '')
        
        logger.info(f"WhatsApp message from {sender}: {text}")
        
        # In a real implementation, we would route this to agent_service.orchestrate_query
        return {
            "sender": sender,
            "query": text,
            "channel": "whatsapp"
        }

    def send_scheme_info(self, to_number, scheme_data):
        """
        Sends a structured message template with scheme details.
        """
        logger.info(f"Sending WhatsApp scheme info to {to_number}")
        # Simulate API call to Meta Graph API
        return {"status": "message_queued", "to": to_number}
