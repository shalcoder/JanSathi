"""
JanSathi Agentic Telecom Automation System (10-Layer Pipeline)
Serves as the master execution function bridging all conceptual layers.
"""
from typing import Dict, Any

from app.automation.l1_integration.schema import UnifiedEventObject
from app.automation.l8_security.guardrails import SecurityGuardrail
from app.automation.l2_ingestion.preprocess import IngestionPipeline
from app.automation.l4_decision.engine import DecisionEngine
from app.automation.l6_action.executor import ActionExecutor
from app.automation.l7_notification.sms import SmsNotifier
from app.automation.l9_observability.logger import get_structured_logger

logger = get_structured_logger("JanSathiAutomation_Orchestrator")

def execute_automation_pipeline(event: UnifiedEventObject) -> Dict[str, Any]:
    """
    The master entry point. Replaces legacy agent loops with the 10-Layer Architecture.
    """
    logger.info("--- STARTING 10-LAYER AUTOMATION CYCLE ---", layer="5_Orchestration", session_id=event.session_id)
    
    # LAYER 8: Security & Consent Gate
    if not SecurityGuardrail.validate_ingress(event):
        return {"action": "REJECT", "reason": "Missing Consent"}
        
    # LAYER 2: Ingestion & Normalization
    structured_input = IngestionPipeline.process(event)
    
    # LAYER 3 & 4: Hybrid Intelligence & Decision Engine
    decision = DecisionEngine.decide(structured_input)
    
    # LAYER 5: Workflow (In production, this proxies to AWS Step Functions)
    # Moving state to Layer 6 Action Exec
    
    # LAYER 6: Action Execution
    action_result = ActionExecutor.execute(decision, event.session_id, 
                                           structured_input.intent_candidate, 
                                           structured_input.user_context)
                                           
    # LAYER 7: Notification Outreach
    if action_result and "receipt" in action_result:
        phone = event.user_context.get("phone_e164") or event.channel_metadata.get("slots", {}).get("callerNumber")
        if phone:
            SmsNotifier.send_confirmation(phone, action_result["receipt"], event.language, event.session_id)
            
    logger.info("--- COMPLETED 10-LAYER AUTOMATION CYCLE ---", layer="5_Orchestration", session_id=event.session_id)
    
    return {
        "decision": decision,
        "action_result": action_result
    }
