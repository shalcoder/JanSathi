import os

VALID_INTENTS = {
    "scheme_lookup",
    "eligibility_check",
    "document_required",
    "general_query",
    "fallback"
}

class BaseIntentClassifier:
    """
    Abstract Base Class for Intent Classifiers.
    All specific classification strategies must inherit from this class.
    
    All classifiers must return a dictionary with:
    - "intent": (str) must be in VALID_INTENTS
    - "confidence": (float) 0.0 to 1.0
    """
    def classify(self, query: str) -> dict:
        """
        Method to be implemented by sub-classes to classify a query.
        """
        raise NotImplementedError


class RuleBasedIntentClassifier(BaseIntentClassifier):
    """
    Rule-Based Intent Classifier strategy.
    
    This is a temporary mock classifier used for keyword-based intent detection.
    It exists as a baseline implementation before Bedrock integration.
    """
    def classify(self, query: str) -> dict:
        msg = query.lower()

        if "eligible" in msg or "eligibility" in msg:
            intent = "eligibility_check"
        elif "document" in msg or "documents" in msg:
            intent = "document_required"
        elif "scheme" in msg or "yojana" in msg:
            intent = "scheme_lookup"
        else:
            intent = "general_query"

        return {
            "intent": intent,
            "confidence": 0.80
        }


class BedrockIntentClassifier(BaseIntentClassifier):
    """
    Bedrock-Based Intent Classifier strategy.

    This strategy will use AWS Bedrock (Claude) for semantic intent classification.
    Currently, it is a placeholder and will raise a NotImplementedError until 
    the AWS integration is completed.
    """
    def classify(self, query: str) -> dict:
        raise NotImplementedError(
            "BedrockIntentClassifier not implemented. "
            "AWS integration must be completed."
        )


class IntentService:
    """
    IntentService — Modular Intent Classification using Strategy Pattern.

    The specific classifier strategy is selected via the INTENT_CLASSIFIER 
    environment variable.
    Values:
    - 'rule_based' (default): Uses keywords to detect intent.
    - 'bedrock': Uses AWS Bedrock (not yet implemented).

    Startup Guard:
    The system intentionally blocks startup if 'bedrock' mode is enabled 
    without a functional implementation. This prevents silent misconfiguration
    in production environments. AWS integration must implement 
    BedrockIntentClassifier before enabling this mode.

    This service decouples the routing logic from the classification strategy,
    allowing seamless switching between implementations.
    It also enforces a structured output contract for all classifiers.
    """
    def __init__(self):
        # Read environment variable for classifier selection
        classifier_type = os.getenv("INTENT_CLASSIFIER", "rule_based")
        
        print(f"[IntentService] Using classifier: {classifier_type}")

        if classifier_type == "rule_based":
            self.classifier = RuleBasedIntentClassifier()
        elif classifier_type == "bedrock":
            # Startup Guard: Fail fast if bedrock is selected but not implemented
            raise RuntimeError(
                "INTENT_CLASSIFIER is set to 'bedrock' but BedrockIntentClassifier is not implemented. "
                "Complete AWS integration before enabling this mode."
            )
        else:
            raise ValueError(f"Invalid INTENT_CLASSIFIER value: {classifier_type}")

    def _validate_output(self, result: dict) -> dict:
        """
        Validates the output from the classifier strategy.
        Ensures the 'intent' is valid and 'confidence' is a properly 
        formatted float. Prevents malformed responses from reaching 
        the router layer.

        :param result: The raw output dictionary from a classifier.
        :return: A validated output dictionary or a safe fallback.
        """
        try:
            intent = result.get("intent")
            confidence = result.get("confidence")

            # Validation Rules
            if intent not in VALID_INTENTS:
                raise ValueError(f"Invalid intent detected: {intent}")
            
            if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
                raise ValueError(f"Invalid confidence score: {confidence}")

            return {
                "intent": intent,
                "confidence": float(confidence)
            }
        except (ValueError, TypeError, AttributeError):
            # Safe Fallback for malformed or invalid results
            return {
                "intent": "fallback",
                "confidence": 0.0
            }

    def classify_intent(self, query: str) -> dict:
        """
        Public API for intent classification.
        Delegates classification to the strategy and validates the output 
        against the structured contract.
        """
        result = self.classifier.classify(query)
        return self._validate_output(result)
