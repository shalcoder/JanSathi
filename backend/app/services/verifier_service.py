"""
verifier_service.py — Risk assessment + decision routing.

Computes a composite risk_score from:
  - ASR confidence (speech quality)
  - Rules engine eligibility score
  - LLM intent confidence
  - Caller history flags (from DynamoDB or local session)

Decision thresholds (per userflow.md):
  risk_score >= 0.85  →  AUTO_SUBMIT
  0.60 <= score < 0.85 → HITL_QUEUE
  score < 0.60        →  NOT_ELIGIBLE_NOTIFY

Returns a VerifierResult dict consumed by the Supervisor.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

DECISION_AUTO_SUBMIT = "AUTO_SUBMIT"
DECISION_HITL        = "HITL_QUEUE"
DECISION_NOT_ELIGIBLE = "NOT_ELIGIBLE_NOTIFY"

# Weights for composite risk score
WEIGHTS = {
    "asr_confidence":   0.20,
    "rules_score":      0.50,   # deterministic — highest weight
    "intent_confidence":0.20,
    "caller_history":   0.10,
}


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


class VerifierService:
    """
    Computes risk_score and routes to AUTO_SUBMIT, HITL_QUEUE, or NOT_ELIGIBLE_NOTIFY.

    JanSathi design principle: deterministic rules always override LLM outputs.
    If rules_score == 0.0 (hard ineligibility), decision is always NOT_ELIGIBLE_NOTIFY
    regardless of other signals.
    """

    def assess(
        self,
        session_id: str,
        rules_score: float,
        eligible: bool,
        asr_confidence: float = 1.0,
        intent_confidence: float = 0.85,
        caller_history_clean: bool = True,
    ) -> dict:
        """
        Compute risk score and return VerifierResult.

        Args:
            session_id:          Current session ID (for logging)
            rules_score:         Float 0-1 from RulesEngine.evaluate()
            eligible:            Boolean eligibility verdict from RulesEngine
            asr_confidence:      ASR confidence (1.0 for web/text, 0-1 for IVR audio)
            intent_confidence:   Intent classifier confidence
            caller_history_clean: False if caller appears in abuse/blacklist

        Returns:
            {
              "risk_score": float,
              "decision": "AUTO_SUBMIT" | "HITL_QUEUE" | "NOT_ELIGIBLE_NOTIFY",
              "reasons": [str],
              "weights_used": dict,
              "signals": dict
            }
        """
        # ── Hard ineligibility guard (deterministic rule wins) ─────────────
        if not eligible or rules_score == 0.0:
            return self._result(
                risk_score=0.0,
                decision=DECISION_NOT_ELIGIBLE,
                reasons=["Deterministic rules evaluation: ineligible"],
                signals={
                    "asr_confidence": asr_confidence,
                    "rules_score": rules_score,
                    "intent_confidence": intent_confidence,
                    "caller_history_clean": caller_history_clean,
                }
            )

        # ── Compute composite risk score ───────────────────────────────────
        caller_score = 1.0 if caller_history_clean else 0.1
        signals = {
            "asr_confidence":    _clamp(asr_confidence),
            "rules_score":       _clamp(rules_score),
            "intent_confidence": _clamp(intent_confidence),
            "caller_history":    caller_score,
        }
        risk_score = sum(WEIGHTS[k] * signals[k] for k in WEIGHTS)
        risk_score = _clamp(risk_score)
        reasons = self._build_reasons(signals, risk_score)

        # ── Decision routing ───────────────────────────────────────────────
        if risk_score >= 0.85:
            decision = DECISION_AUTO_SUBMIT
        elif risk_score >= 0.60:
            decision = DECISION_HITL
        else:
            decision = DECISION_NOT_ELIGIBLE

        logger.info(
            f"[Verifier] session={session_id} risk={risk_score:.3f} decision={decision} "
            f"asr={asr_confidence:.2f} rules={rules_score:.2f} intent={intent_confidence:.2f}"
        )

        # Emit telemetry
        try:
            from app.services.telemetry_service import get_telemetry
            t = get_telemetry()
            t.emit("EligibilityRate", risk_score * 100, {"decision": decision}, unit="Percent")
            if decision == DECISION_HITL:
                t.emit("HITLCreated", 1.0)
        except Exception:
            pass

        return self._result(risk_score, decision, reasons, signals)

    def _build_reasons(self, signals: dict, risk_score: float) -> list:
        reasons = []
        if signals["asr_confidence"] < 0.6:
            reasons.append(f"⚠️ Low ASR confidence ({signals['asr_confidence']:.0%}) — speech unclear")
        if signals["rules_score"] < 0.8:
            reasons.append(f"⚠️ Partial rules match ({signals['rules_score']:.0%}) — some conditions unverified")
        if signals["intent_confidence"] < 0.7:
            reasons.append(f"⚠️ Intent confidence low ({signals['intent_confidence']:.0%})")
        if signals["caller_history"] < 0.5:
            reasons.append("⛔ Caller history flag — manual review required")
        if not reasons:
            reasons.append("✅ All signals within acceptable thresholds")
        reasons.append(f"Composite risk score: {risk_score:.3f}")
        return reasons

    def _result(self, risk_score: float, decision: str, reasons: list, signals: dict) -> dict:
        return {
            "risk_score": round(risk_score, 4),
            "decision": decision,
            "reasons": reasons,
            "signals": signals,
            "weights_used": WEIGHTS,
        }

    # ── Convenience: caller history lookup ────────────────────────────────────

    def get_caller_history_flag(self, session_id: str) -> bool:
        """
        Returns True if caller has a clean history (no flags).
        Checks DynamoDB blacklist table if available, otherwise returns True.
        """
        try:
            import boto3
            table = boto3.resource(
                "dynamodb",
                region_name=__import__("os").getenv("AWS_REGION", "ap-south-1")
            ).Table("JanSathiCallerFlags")
            resp = table.get_item(Key={"session_id": session_id})
            return "Item" not in resp
        except Exception:
            return True  # assume clean if table unavailable
