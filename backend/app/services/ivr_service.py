from app.core.utils import logger
import os

class IVRService:
    """
    Handling Voice-First interactions via Twilio/Standard IVR.
    Generates TwiML for dynamic voice response.
    """
    def __init__(self):
        self.enabled = os.getenv("TWILIO_ACCOUNT_SID") is not None

    def generate_twiml(self, text, language='hi-IN'):
        """
        Creates a TwiML response to 'Say' the text in the correct dialect.
        Uses Amazon Polly via Twilio if configured.
        """
        # Mapping standard codes to Twilio/Polly voice codes
        voice_map = {
            'hi': 'Aditi',
            'ta': 'Valluvar',
            'kn': 'Kajal'
        }
        voice = voice_map.get(language[:2], 'Aditi')
        
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="Polly.{voice}" language="{language}">{text}</Say></Response>'
        return twiml

    def handle_incoming_call(self, from_number):
        logger.info(f"Incoming IVR call from {from_number}")
        # Logic to fetch user profile by phone number (KYC integration)
        return {
            "is_returning": True,
            "message": "Namaste! Welcome back to JanSathi. How can I help you with government schemes today?"
        }
