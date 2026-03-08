import os
import json
import logging

logger = logging.getLogger(__name__)

VALID_INTENTS = {
    "apply",
    "info",
    "grievance",
    "track",
    "life_event",
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

    SCHEME_APPLY_KEYWORDS = [
        "kisan", "किसान", "pm kisan", "pmkisan", "samman nidhi",
        "awas", "आवास", "pm awas", "housing scheme", "makaan",
        "shram", "श्रम", "e shram", "eshram", "labour card",
    ]
    APPLY_KEYWORDS = [
        "apply", "application", "आवेदन", "अप्लाई", "register", "sign up",
        "enroll", "eligible", "eligibility", "पात्रता", "yojana apply",
        "scheme apply", "want to get", "how to get", "check eligibility",
        "patrata", "labh", "लाभ", "benefit check",
    ]
    INFO_KEYWORDS = [
        "what is", "tell me", "explain", "how does", "क्या है", "बताइए",
        "जानकारी", "info", "details", "scheme details", "yojana details",
        "documents", "documents required", "documents needed",
    ]
    GRIEVANCE_KEYWORDS = [
        "grievance", "complaint", "शिकायत", "problem", "issue", "not received",
        "pending", "rejected", "wrong", "error", "correction",
        "payment nahi", "paisa nahi", "पैसे नहीं", "नहीं आया",
        "haven't received", "didn't receive",
    ]
    TRACK_KEYWORDS = [
        "track", "status", "स्थिति", "application status",
        "case status", "where is my", "case id", "check status",
        "mera status", "meri application",
    ]
    LIFE_EVENT_KEYWORDS = {
        "crop_loss": [
            "crop failed", "crop loss", "fasal kharab", "फसल खराब", "my crop failed",
            "pest attack", "drought loss", "crop damaged",
        ],
        "child_birth": [
            "baby was born", "new child", "child birth", "delivery happened", "बच्चा हुआ",
            "newborn", "birth certificate for baby",
        ],
        "job_loss": [
            "lost my job", "job loss", "no work", "काम छूट गया", "unemployed",
            "laid off", " बेरोजगार", " बेरोज़गार",
        ],
    }

    def _detect_life_event(self, msg: str) -> str:
        for event_key, terms in self.LIFE_EVENT_KEYWORDS.items():
            if any(term in msg for term in terms):
                return event_key
        return "unknown"

    def classify(self, query: str, language: str = "hi") -> dict:
        msg = query.lower()
        detected_event = self._detect_life_event(msg)
        if detected_event != "unknown":
            return {
                "intent": "life_event",
                "confidence": 0.92,
                "language_detected": language,
                "scheme_hint": "unknown",
                "event_key": detected_event,
            }

        # Scheme-specific apply keywords take HIGHEST priority
        if any(k in msg for k in self.SCHEME_APPLY_KEYWORDS):
            # Detect which scheme
            if any(k in msg for k in ("kisan", "किसान", "samman nidhi", "pmkisan")):
                return {"intent": "apply", "confidence": 0.90, "language_detected": language, "scheme_hint": "pm_kisan"}
            if any(k in msg for k in ("awas", "आवास", "housing")):
                return {"intent": "apply", "confidence": 0.90, "language_detected": language, "scheme_hint": "pm_awas_urban"}
            if any(k in msg for k in ("shram", "श्रम", "labour")):
                return {"intent": "apply", "confidence": 0.90, "language_detected": language, "scheme_hint": "e_shram"}
            return {"intent": "apply", "confidence": 0.85, "language_detected": language, "scheme_hint": "unknown"}

        if any(k in msg for k in self.GRIEVANCE_KEYWORDS):
            return {"intent": "grievance", "confidence": 0.85, "language_detected": language, "scheme_hint": "unknown"}
        if any(k in msg for k in self.TRACK_KEYWORDS):
            return {"intent": "track", "confidence": 0.82, "language_detected": language, "scheme_hint": "unknown"}
        if any(k in msg for k in self.APPLY_KEYWORDS):
            return {"intent": "apply", "confidence": 0.80, "language_detected": language, "scheme_hint": "unknown"}
        if any(k in msg for k in self.INFO_KEYWORDS):
            return {"intent": "info", "confidence": 0.78, "language_detected": language, "scheme_hint": "unknown"}

        return {"intent": "info", "confidence": 0.60, "language_detected": language, "scheme_hint": "unknown"}


class BedrockIntentClassifier(BaseIntentClassifier):
    """
    Bedrock (Nova Micro) intent + language classifier.
    Uses Amazon Nova Micro via the Converse API — fast and cheap.
    Falls back to RuleBasedIntentClassifier on any AWS error.
    """

    NOVA_MICRO_MODEL = "amazon.nova-micro-v1:0"

    CLASSIFY_PROMPT = """You are an intent classifier for JanSathi, India's AI-powered civic assistance IVR system.

Classify the following user utterance and return ONLY a valid JSON object (no preamble, no explanation):

{{
  "intent": "<apply|info|grievance|track|life_event|fallback>",
  "confidence": <0.0-1.0>,
  "language_detected": "<hi|ta|kn|en|other>",
  "required_slots": ["<slot1>", "<slot2>"],
  "scheme_hint": "<pm_kisan|pm_awas_urban|e_shram|unknown>",
  "event_key": "<crop_loss|child_birth|job_loss|unknown>"
}}

INTENT DEFINITIONS:
- apply: user wants to apply for a government scheme or check eligibility
- info: user wants information about a scheme, documents, or process
- grievance: user has a complaint or problem (payment not received, rejection, etc.)
- track: user wants to check status of an existing application or case
- life_event: user describes a life event that should trigger a civic workflow (crop loss, child birth, job loss)
- fallback: unclear or off-topic

USER UTTERANCE: {query}"""

    def __init__(self):
        self._bedrock = None
        self._fallback = RuleBasedIntentClassifier()
        self._init_bedrock()

    def _init_bedrock(self):
        try:
            import boto3
            region = os.getenv("AWS_REGION", "ap-south-1")
            self._bedrock = boto3.client("bedrock-runtime", region_name=region)
            logger.info("[BedrockIntentClassifier] Nova Micro client initialised")
        except Exception as e:
            logger.warning(f"[BedrockIntentClassifier] Bedrock unavailable, will use rule-based: {e}")
            self._bedrock = None

    def classify(self, query: str, language: str = "hi") -> dict:
        if not self._bedrock:
            return self._fallback.classify(query, language)

        prompt = self.CLASSIFY_PROMPT.format(query=query)

        # Nova Micro via Converse API (NOT invoke_model)
        try:
            response = self._bedrock.converse(
                modelId=self.NOVA_MICRO_MODEL,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 256, "temperature": 0.0},
            )
            text = response["output"]["message"]["content"][0]["text"].strip()

            # Strip markdown fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

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
                "event_key": result.get("event_key", "unknown"),
            }
        except Exception as e:
            logger.warning(f"[BedrockIntentClassifier] Nova Micro call failed, falling back: {e}")
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
                "event_key": result.get("event_key", "unknown"),
            }
        except Exception:
            return {"intent": "fallback", "confidence": 0.0, "language_detected": "hi", "required_slots": [], "scheme_hint": "unknown", "event_key": "unknown"}

    def classify_intent(self, query: str) -> dict:
        """Legacy entry point (no language param) — kept for backward compat."""
        result = self.classifier.classify(query, language="hi")
        return self._validate(result)

    def classify_intent_ivr(self, query: str, language: str = "hi") -> dict:
        """IVR-aware entry point — passes language for multilingual Bedrock prompt."""
        result = self.classifier.classify(query, language=language)
        return self._validate(result)
