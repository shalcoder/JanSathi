"""
Layer 3 Intelligence: Hybrid Brain Architecture
Split into Rule-Based Brain and Learning-Based Brain for deterministic safety.
"""
from typing import Dict, Any, Tuple
from app.automation.l2_ingestion.schema import StructuredInput
from app.automation.l9_observability.logger import get_structured_logger

logger = get_structured_logger("JanSathiAutomation_L3_Rules")

class RuleBasedBrain:
    """
    Deterministic rules engine. Checks hard constraints completely avoiding LLM hallucination.
    """
    @staticmethod
    def evaluate_pm_kisan(slots: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Hard rules for PM Kisan:
        - Must be farmer
        - Land <= 2 hectares (approx 5 acres)
        """
        occupation = str(context.get("occupation", slots.get("occupation", ""))).lower()
        if occupation and "farmer" not in occupation:
            return False, "Not eligible: Occupation must be Farmer."
            
        land_acres = str(context.get("land_holding_acres", slots.get("land_holding_acres", "0")))
        try:
            if float(land_acres) > 5.0:
                return False, f"Not eligible: Land holding {land_acres} exceeds 5 acres limit."
        except ValueError:
            pass # Unknown, need to collect slot
            
        return True, "Eligible based on deterministic rules."

    @classmethod
    def process(cls, input_data: StructuredInput) -> Dict[str, Any]:
        """Runs all applicable deterministic rules based on intent."""
        logger.info(f"Running deterministic rules for intent: {input_data.intent_candidate}", layer="3_Intelligence")
        
        result = {"passed_rules": True, "reason": "No strict rules triggered."}
        
        if input_data.intent_candidate == "APPLY_PM_KISAN":
            passed, reason = cls.evaluate_pm_kisan(input_data.slots_detected, input_data.user_context)
            result = {"passed_rules": passed, "reason": reason}
            
        logger.info(f"Rule evaluation result: {result['passed_rules']}", layer="3_Intelligence")
        return result
