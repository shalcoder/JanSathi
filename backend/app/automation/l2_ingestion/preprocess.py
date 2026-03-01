"""
Layer 2 Ingestion: Preprocessing and Normalization
"""
import re
from typing import Dict, Any, Tuple
from app.automation.l1_integration.schema import UnifiedEventObject
from app.automation.l2_ingestion.schema import StructuredInput
from app.automation.l9_observability.logger import get_structured_logger

logger = get_structured_logger("JanSathiAutomation_L2")

class IngestionPipeline:
    """
    Cleans, normalizes and pre-processes the UnifiedEventObject into a StructuredInput.
    Handles PII masking and basic string normalization.
    """
    
    @staticmethod
    def _mask_pii(text: str) -> Tuple[str, bool]:
        """
        Simple heuristic PII masking (Aadhaar, Phones).
        """
        masked = False
        # Aadhaar (12 digits)
        aadhaar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
        if re.search(aadhaar_pattern, text):
            text = re.sub(aadhaar_pattern, '[AADHAAR_MASKED]', text)
            masked = True
            
        # Phone numbers (10 digits)
        phone_pattern = r'\b[6-9]\d{9}\b'
        if re.search(phone_pattern, text):
            text = re.sub(phone_pattern, '[PHONE_MASKED]', text)
            masked = True
            
        return text, masked
        
    @staticmethod
    def _normalize_text(text: str) -> str:
        # Strip extra whitespace and lower case for basic normalization
        return " ".join(text.split()).strip()

    @classmethod
    def process(cls, event: UnifiedEventObject) -> StructuredInput:
        """
        Converts a UnifiedEventObject into a Layer 2 StructuredInput.
        """
        logger.info(f"Starting Layer 2 Ingestion for channel {event.channel}", 
                    layer="2_Ingestion", session_id=event.session_id)
        
        raw_text = event.message
        clean_text = cls._normalize_text(raw_text)
        safe_text, is_pii_masked = cls._mask_pii(clean_text)
        
        if is_pii_masked:
            logger.warn("PII detected and masked during ingestion.", 
                        layer="2_Ingestion", session_id=event.session_id)
                        
        # Basic intent heuristics (fallback before LLM)
        intent_candidate = "UNKNOWN"
        lower_safe = safe_text.lower()
        if any(w in lower_safe for w in ["pm kisan", "farmer", "agriculture", "kisan"]):
            intent_candidate = "APPLY_PM_KISAN"
            
        structured = StructuredInput(
            intent_candidate=intent_candidate,
            slots_detected=event.channel_metadata.get("slots", {}),
            confidence=event.channel_metadata.get("asr_confidence", 1.0),
            is_pii_masked=is_pii_masked,
            clean_message=safe_text,
            user_context=event.user_context
        )
        
        logger.info(f"Ingestion complete. Intent candidate: {intent_candidate}", 
                    layer="2_Ingestion", session_id=event.session_id)
                    
        return structured
