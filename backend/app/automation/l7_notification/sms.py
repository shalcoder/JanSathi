"""
Layer 7: Notification and Outreach
Abstracts SNS and Pinpoint SMS dispatch.
"""
from typing import Dict, Any
from app.automation.l9_observability.logger import get_structured_logger
import logging

logger = get_structured_logger("JanSathiAutomation_L7")

class SmsNotifier:
    """
    Handles SMS dispatching for the end-user loop closure.
    """
    
    @classmethod
    def _format_receipt_sms(cls, receipt: Dict[str, Any], language: str) -> str:
        """
        Formats the SMS string. Multi-lingual support included.
        """
        # Simulated multi-lingual translation wrapper
        if language == "hi":
            return f"Namaste. Aapka JanSathi status verified hai. Receipt Number: {receipt['receipt_id']}. CSC jaayein."
        return f"Hello. Your JanSathi status is verified. Receipt Number: {receipt['receipt_id']}. Please visit your local CSC."

    @classmethod
    def send_confirmation(cls, phone_number: str, receipt: Dict[str, Any], language: str, session_id: str) -> bool:
        """
        Dispatches the confirmation to AWS SNS.
        """
        if not phone_number:
            logger.warn("Skipping SMS dispatch: No phone number provided in context.", 
                        layer="7_Notification", session_id=session_id)
            return False
            
        message = cls._format_receipt_sms(receipt, language)
        
        logger.info(f"Dispatching SMS to {phone_number}: '{message}'", 
                    layer="7_Notification", session_id=session_id)
                    
        import boto3
        import os
        
        try:
            # Send via AWS SNS using the region specified in the environment
            region = os.getenv("AWS_REGION", "ap-south-1")
            sns = boto3.client('sns', region_name=region)
            sns.publish(PhoneNumber=phone_number, Message=message)
            logger.info(f"Successfully dispatched real SMS via SNS to {phone_number}", 
                        layer="7_Notification", session_id=session_id)
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch real SMS via SNS to {phone_number}: {e}", 
                        layer="7_Notification", session_id=session_id)
            return False
