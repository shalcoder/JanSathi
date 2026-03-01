import os
import json
import logging

logger = logging.getLogger(__name__)

VALID_INTENTS = {
    "apply",
    "info",
    "grievance",
    "track",
    # legacy aliases kept for backward compat
    "scheme_lookup",
    "eligibility_check",
    "document_required",
    "general_query",
    "fallback",
}

# Mapping legacy intents → unified intents
INTENT_ALIAS = {
    "scheme_lookup": "info",
    "eligibility_check": "apply",
    "document_required": "info",
    "general_query": "info",
}


class BaseIntentClassifier:
    """Abstract base — all classifiers must return intent + confidence."""
    def classify(self, query: str, language: str = "hi") -> dict:
        raise NotImplementedError


class RuleBasedIntentClassifier(BaseIntentClassifier):
    """Fast keyword-based fallback classifier (no cloud dependency)."""

    APPLY_KEYWORDS = [
        "apply", "application", "आवेदन", "अप्लाई", "register", "sign up",
        "enroll", "eligible", "eligibility", "पात्रता", "yojana apply",
        "scheme apply", "want to get", "how to get", "kisan", "किसान",
    ]
    INFO_KEYWORDS = [
        "what is", "tell me", "explain", "how does", "क्या है", "बताइए",
        "जानकारी", "info", "details", "scheme details", "yojana details",
        "documents", "documents required", "documents needed",
    ]
    GRIEVANCE_KEYWORDS = [
        "grievance", "complaint", "शिकायत", "problem", "issue", "not received",
        "pending", "rejected", "wrong", "error", "correction",
    ]
    TRACK_KEYWORDS = [
        "track", "status", "स्थिति", "check", "application status",
        "case status", "where is my", "case id",
    ]

    def classify(self, query: str, language: str = "hi") -> dict:
        msg = query.lower()

        if any(k in msg for k in self.TRACK_KEYWORDS):
            return {"intent": "track", "confidence": 0.85, "language_detected": language}
        if any(k in msg for k in self.GRIEVANCE_KEYWORDS):
            return {"intent": "grievance", "confidence": 0.82, "language_detected": language}
        if any(k in msg for k in self.APPLY_KEYWORDS):
            return {"intent": "apply", "confidence": 0.80, "language_detected": language}
        if any(k in msg for k in self.INFO_KEYWORDS):
            return {"intent": "info", "confidence": 0.78, "language_detected": language}

        return {"intent": "info", "confidence": 0.60, "language_detected": language}


class BedrockIntentClassifier(BaseIntentClassifier):
    """
    Bedrock (Claude Haiku) intent + language classifier.
    Returns: intent, confidence, language_detected, required_slots.
    Falls back to RuleBasedIntentClassifier on any AWS error.
    """

    HAIKU_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"

    CLASSIFY_PROMPT = """You are an intent classifier for a multilingual Indian government services IVR system.

Classify the following user utterance and return ONLY a JSON object (no preamble, no explanation):

{{
  "intent": "<apply|info|grievance|track|fallback>",
  "confidence": <0.0-1.0>,
  "language_detected": "<hi|ta|kn|en|other>",
  "required_slots": ["<slot1>", "<slot2>"],
  "scheme_hint": "<pm_kisan|pm_awas_urban|e_shram|unknown>"
}}

INTENT DEFINITIONS:
- apply: user wants to apply for a government scheme or check eligibility
- info: user wants information about a scheme, documents, or process
- grievance: user has a complaint or problem (payment not received, rejection, etc.)
- track: user wants to check status of an existing application or case
- fallback: unclear or off-topic

USER UTTERANCE: {query}
"""

    def __init__(self):
        self._bedrock = None
        self._fallback = RuleBasedIntentClassifier()
        self._init_bedrock()

    def _init_bedrock(self):
        try:
            import boto3
            region = os.getenv("AWS_REGION", "ap-south-1")
            self._bedrock = boto3.client("bedrock-runtime", region_name=region)
            logger.info("[BedrockIntentClassifier] Client initialised")
        except Exception as e:
            logger.warning(f"[BedrockIntentClassifier] Bedrock unavailable, will use rule-based: {e}")
            self._bedrock = None

    def classify(self, query: str, language: str = "hi") -> dict:
        if not self._bedrock:
            return self._fallback.classify(query, language)

        prompt = self.CLASSIFY_PROMPT.format(query=query)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 256,
            "temperature": 0.0,
            "messages": [{"role": "user", "content": prompt}],
        })

        try:
            response = self._bedrock.invoke_model(
                body=body,
                modelId=self.HAIKU_MODEL,
                accept="application/json",
                contentType="application/json",
            )
            text = json.loads(response["body"].read())["content"][0]["text"].strip()
            result = json.loads(text)
            intent = result.get("intent", "info")
            confidence = float(result.get("confidence", 0.75))
            lang_detected = result.get("language_detected", language)
            return {
                "intent": intent,
                "confidence": confidence,
                "language_detected": lang_detected,
                "required_slots": result.get("required_slots", []),
                "scheme_hint": result.get("scheme_hint", "unknown"),
            }
        except Exception as e:
            logger.warning(f"[BedrockIntentClassifier] Bedrock call failed, falling back: {e}")
            return self._fallback.classify(query, language)


class IntentService:
    """
    Modular intent classification — rule_based (default) or bedrock.
    Controlled via INTENT_CLASSIFIER env var.
    """

    def __init__(self):
        classifier_type = os.getenv("INTENT_CLASSIFIER", "rule_based")
        logger.info(f"[IntentService] Using classifier: {classifier_type}")

        if classifier_type == "bedrock":
            self.classifier = BedrockIntentClassifier()
        elif classifier_type == "rule_based":
            self.classifier = RuleBasedIntentClassifier()
        else:
            raise ValueError(f"Invalid INTENT_CLASSIFIER: {classifier_type}")

    def _validate(self, result: dict) -> dict:
        try:
            intent = INTENT_ALIAS.get(result.get("intent"), result.get("intent"))
            confidence = float(result.get("confidence", 0.0))
            if intent not in VALID_INTENTS:
                raise ValueError(f"Invalid intent: {intent}")
            if not 0.0 <= confidence <= 1.0:
                raise ValueError(f"Invalid confidence: {confidence}")
            return {
                "intent": intent,
                "confidence": confidence,
                "language_detected": result.get("language_detected", "hi"),
                "required_slots": result.get("required_slots", []),
                "scheme_hint": result.get("scheme_hint", "unknown"),
            }
        except Exception:
            return {"intent": "fallback", "confidence": 0.0, "language_detected": "hi", "required_slots": [], "scheme_hint": "unknown"}

    def classify_intent(self, query: str) -> dict:
        """Legacy entry point (no language param) — kept for backward compat."""
        result = self.classifier.classify(query, language="hi")
        return self._validate(result)

    def classify_intent_ivr(self, query: str, language: str = "hi") -> dict:
        """IVR-aware entry point — passes language for multilingual Bedrock prompt."""
        result = self.classifier.classify(query, language=language)
        return self._validate(result)
