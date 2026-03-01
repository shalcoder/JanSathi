"""
Layer 4 Decision Engine
Aggregates Layer 3 intel to make final routing decision.
"""
from enum import Enum
from typing import Dict, Any
from app.automation.l2_ingestion.schema import StructuredInput
from app.automation.l9_observability.logger import get_structured_logger
from app.automation.l3_intelligence.rules import RuleBasedBrain
from app.automation.l3_intelligence.llm import LearningBasedBrain

logger = get_structured_logger("JanSathiAutomation_L4")

class DecisionAction(str, Enum):
    AUTO_PROCEED = "AUTO_PROCEED"
    ESCALATE_TO_HITL = "ESCALATE_TO_HITL"
    REJECT_WITH_REASON = "REJECT_WITH_REASON"
    REQUEST_MORE_SLOTS = "REQUEST_MORE_SLOTS"

class DecisionEngine:
    """
    Layer 4: Decision Engine.
    Aggregates LLM confidence, Rule Results, and determines risk.
    """
    
    @classmethod
    def calculate_risk(cls, rule_result: Dict[str, Any], llm_result: Dict[str, Any]) -> float:
        """Calculates a risk score from 0.0 to 1.0"""
        risk = 0.0
        if not rule_result.get("passed_rules"):
            risk += 0.8
        if llm_result.get("llm_confidence", 0) < 0.7:
            risk += 0.4
        return min(1.0, risk)

    @classmethod
    def decide(cls, input_data: StructuredInput) -> Dict[str, Any]:
        """
        Runs the full Hybrid Intelligence stack and dictates the workflow action.
        """
        logger.info("Starting Decision Engine Convergence.", layer="4_Decision")
        
        # 1. Run Layer 3 Intel
        rule_results = RuleBasedBrain.process(input_data)
        llm_results = LearningBasedBrain.process(input_data)
        
        # 2. Risk Calculation
        risk_score = cls.calculate_risk(rule_results, llm_results)
        
        # 3. Decision Matrix
        action = DecisionAction.AUTO_PROCEED
        reason = "All checks passed."
        
        if not rule_results["passed_rules"]:
            action = DecisionAction.REJECT_WITH_REASON
            reason = rule_results["reason"]
        elif risk_score > 0.7:
            action = DecisionAction.ESCALATE_TO_HITL
            reason = "High risk score detected; manual oversight required."
        elif llm_results["llm_intent"] in ["APPLY_PM_KISAN"]:
            has_land = bool(input_data.slots_detected.get("land_holding_acres") or input_data.user_context.get("land_holding_acres"))
            if not has_land:
                action = DecisionAction.REQUEST_MORE_SLOTS
                reason = "Missing schema slot: land_holding_acres"
            
        logger.warn(f"Decision REACHED: {action.value} | Risk: {risk_score}", layer="4_Decision")
        
        return {
            "action": action.value,
            "reason": reason,
            "risk_score": risk_score,
            "llm_intent_agreed": llm_results["llm_intent"]
        }
