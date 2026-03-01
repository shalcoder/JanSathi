"""
fl_service.py — DEPRECATED / OUT OF SCOPE

Federated Learning (Flower/flwr) was removed from JanSathi architecture.

From agents.md § "What You DO NOT Need Now":
  ❌ Federated learning agent
  ❌ Multi-agent reasoning drama

This stub is kept only to avoid import errors in legacy routes
that still reference it. No new code should import this.

For model telemetry & analytics use telemetry_service.py.
"""

import logging
logger = logging.getLogger(__name__)


class FederatedLearningService:
    """Deprecated — returns mock metrics for backward compat only."""

    def __init__(self, *args, **kwargs):
        logger.warning(
            "[FLService] FederatedLearningService is deprecated and OUT OF SCOPE. "
            "Use telemetry_service.TelemetryService for metrics."
        )
        self.mock_mode = True
        self.current_round = 0

    def start_server(self, *args, **kwargs):
        logger.warning("[FLService] start_server() called on deprecated stub — no-op.")

    def get_metrics(self):
        return {
            "current_round": self.current_round,
            "status": "DEPRECATED — not in JanSathi scope",
            "active_clients": 0,
        }

    def weighted_average(self, metrics):
        return {}
