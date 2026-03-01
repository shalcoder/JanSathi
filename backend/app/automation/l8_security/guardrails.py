"""
Layer 8 Security: Governance, Validation, and Masking abstraction.
"""
from typing import Dict, Any
from app.automation.l1_integration.schema import UnifiedEventObject
from app.automation.l9_observability.logger import get_structured_logger

logger = get_structured_logger("JanSathiAutomation_L8")

class SecurityGuardrail:
    """
    Evaluates events and actions against strictly enforced IAM,
    Consent, and Validation protocols before state changes.
    """
    
    @classmethod
    def validate_ingress(cls, event: UnifiedEventObject) -> bool:
        """
        Validates ingress events. If a user did not provide voice consent,
        the system aggressively rejects processing.
        """
        if not event.consent_given:
            logger.error("Security Violation: Processing attempted without explicit user consent.", 
                         layer="8_Security", session_id=event.session_id)
            return False
            
        logger.info("Ingress security checks passed.", layer="8_Security", session_id=event.session_id)
        return True
