"""
telemetry_service.py — CloudWatch metrics emitter for JanSathi.

Emits operational + impact metrics with console-log fallback for local dev.
Used by all agents to give judges / dashboard real KPIs.
"""

import os
import logging
import time
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ── Metric definitions ────────────────────────────────────────────────────────
NAMESPACE = "JanSathi"

METRICS = {
    "CallProcessed":      {"unit": "Count",        "desc": "Total IVR calls processed"},
    "EligibilityRate":    {"unit": "Percent",       "desc": "% callers found eligible"},
    "AvgTurnsPerSession": {"unit": "Count",         "desc": "Average slot-collection turns per call"},
    "HITLCreated":        {"unit": "Count",         "desc": "Cases escalated to human review"},
    "ASRSuccessRate":     {"unit": "Percent",       "desc": "% ASR transcriptions with confidence>=0.6"},
    "BedrockLatencyMs":   {"unit": "Milliseconds",  "desc": "Bedrock API round-trip latency"},
    "SMSDelivered":       {"unit": "Count",         "desc": "SMS notifications sent successfully"},
    "WorkflowStarted":    {"unit": "Count",         "desc": "Step Function executions started"},
    "WorkflowCompleted":  {"unit": "Count",         "desc": "Step Function executions completed"},
    "WebChatQuery":       {"unit": "Count",         "desc": "Web chat queries processed"},
    "SubmissionQueued":   {"unit": "Count",         "desc": "Applications queued for submission"},
    "SubmissionError":    {"unit": "Count",         "desc": "Submission failures (gov API down)"},
    "ConsentCaptured":    {"unit": "Count",         "desc": "User consents recorded"},
    "AuditLogWritten":    {"unit": "Count",         "desc": "Audit entries persisted"},
}

# In-process store for local dev reporting
_local_buffer: list = []


class TelemetryService:
    """
    Emits CloudWatch custom metrics.
    Falls back to console + in-memory buffer when AWS is not configured.
    """

    def __init__(self):
        self._cw = None
        self._namespace = NAMESPACE
        self._region = os.getenv("AWS_REGION", "ap-south-1")
        self._enabled = os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
        self._init_cloudwatch()

    def _init_cloudwatch(self):
        try:
            import boto3
            self._cw = boto3.client("cloudwatch", region_name=self._region)
            logger.info("[Telemetry] CloudWatch client initialised")
        except Exception as e:
            logger.info(f"[Telemetry] CloudWatch unavailable, using console fallback: {e}")
            self._cw = None

    # ── Public API ────────────────────────────────────────────────────────────

    def emit(self, metric_name: str, value: float = 1.0,
             dimensions: Optional[dict] = None, unit: Optional[str] = None) -> None:
        """
        Emit a single metric data point.

        Args:
            metric_name: Must be one of METRICS keys (or custom string)
            value: Numeric value
            dimensions: Dict of {Name: Value} for CloudWatch dimension filtering
            unit: Override unit (defaults to METRICS definition or 'Count')
        """
        if not self._enabled:
            return

        resolved_unit = unit or METRICS.get(metric_name, {}).get("unit", "Count")
        dims = [{"Name": k, "Value": str(v)} for k, v in (dimensions or {}).items()]

        entry = {
            "metric": metric_name,
            "value": value,
            "unit": resolved_unit,
            "dimensions": dimensions or {},
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        _local_buffer.append(entry)

        if self._cw:
            try:
                self._cw.put_metric_data(
                    Namespace=self._namespace,
                    MetricData=[{
                        "MetricName": metric_name,
                        "Dimensions": dims,
                        "Value": value,
                        "Unit": resolved_unit,
                        "Timestamp": datetime.now(timezone.utc),
                    }]
                )
            except Exception as e:
                logger.warning(f"[Telemetry] CloudWatch put failed: {e}")
        else:
            logger.info(f"[TELEMETRY] {metric_name}={value} {resolved_unit} {dimensions or ''}")

    def emit_latency(self, metric_name: str, start_time: float, dimensions: Optional[dict] = None):
        """Helper: emit elapsed milliseconds since start_time = time.perf_counter()."""
        ms = round((time.perf_counter() - start_time) * 1000, 2)
        self.emit(metric_name, ms, dimensions, unit="Milliseconds")
        return ms

    def get_local_metrics(self) -> list:
        """Return in-memory buffer (for local dev dashboard)."""
        return list(_local_buffer)

    def get_summary(self) -> dict:
        """Aggregate in-memory metrics for the health endpoint."""
        from collections import defaultdict
        totals: dict = defaultdict(float)
        counts: dict = defaultdict(int)
        for e in _local_buffer:
            totals[e["metric"]] += e["value"]
            counts[e["metric"]] += 1
        return {k: {"total": totals[k], "count": counts[k]} for k in totals}


# Module-level singleton
_telemetry: Optional[TelemetryService] = None

def get_telemetry() -> TelemetryService:
    """Get or create the module-level TelemetryService singleton."""
    global _telemetry
    if _telemetry is None:
        _telemetry = TelemetryService()
    return _telemetry
