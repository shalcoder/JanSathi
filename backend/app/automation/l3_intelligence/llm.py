"""
Layer 3 Intelligence: Learning-Based Brain 
"""
from typing import Dict, Any
from app.automation.l2_ingestion.schema import StructuredInput
from app.automation.l9_observability.logger import get_structured_logger

logger = get_structured_logger("JanSathiAutomation_L3_LLM")

class LearningBasedBrain:
    """
    Learning-Based Brain utilizing LLMs for intent classification, sentiment, and unstructured extraction.
    Note: Mocked here, assumes Bedrock Client invocation.
    """
    
    @classmethod
    def process(cls, input_data: StructuredInput) -> Dict[str, Any]:
        """
        Re-evaluates intent or extracts missing unstructured slots.
        In production, this calls Haiku for fast turns.
        """
        logger.info(f"Invoking LLM Brain for message: {input_data.clean_message[:20]}...", layer="3_Intelligence")
        
        # Simulated LLM Inference Metadata
        llm_confidence = 0.95
        inferred_intent = input_data.intent_candidate
        
        # If ingestion didn't know, ask LLM
        if inferred_intent == "UNKNOWN":
            prompt = input_data.clean_message.lower()
            if "house" in prompt or "awas" in prompt:
                inferred_intent = "APPLY_AWAS_YOJANA"
            elif "health" in prompt or "ayushman" in prompt:
                inferred_intent = "APPLY_AYUSHMAN"
                
        logger.info(f"LLM Brain resulted in Intent={inferred_intent}, Conf={llm_confidence}", layer="3_Intelligence")
        
        return {
            "llm_intent": inferred_intent,
            "llm_confidence": llm_confidence,
            "sentiment": "Neutral"
        }
