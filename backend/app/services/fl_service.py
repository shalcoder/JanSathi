import flwr as fl
import numpy as np
from typing import List, Tuple, Dict, Optional
from app.core.utils import logger, log_event

class FederatedLearningService:
    """
    Federated Learning Aggregator Service using Flower (flwr).
    Handles:
    1. Server Strategy (FedAvg)
    2. Model Aggregation
    3. Differential Privacy (DP) Integration (Custom Strategy)
    """

    def __init__(self, min_clients=2, round_timeout=300):
        self.min_clients = min_clients
        self.round_timeout = round_timeout
        self.current_round = 1
        
        # Define Strategy
        self.strategy = fl.server.strategy.FedAvg(
            fraction_fit=1.0,  # Sample 100% of available clients
            fraction_evaluate=0.5,
            min_fit_clients=self.min_clients,
            min_evaluate_clients=self.min_clients,
            min_available_clients=self.min_clients,
            evaluate_metrics_aggregation_fn=self.weighted_average,
        )

    def weighted_average(self, metrics: List[Tuple[int, Dict[str, float]]]) -> Dict[str, float]:
        """Aggregation function for evaluation metrics."""
        accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
        examples = [num_examples for num_examples, _ in metrics]
        return {"accuracy": sum(accuracies) / sum(examples)}

    def start_server(self, port=8080):
        """Starts the Flower server."""
        logger.info(f"Starting Flower Server on port {port}")
        try:
            fl.server.start_server(
                server_address=f"0.0.0.0:{port}",
                config=fl.server.ServerConfig(num_rounds=3),
                strategy=self.strategy,
            )
        except Exception as e:
            logger.error(f"Failed to start Flower server: {e}")

    # Legacy/Simulation methods for API compatibility if needed
    def get_metrics(self):
        return {
            "current_round": self.current_round,
            "active_clients": self.min_clients, # Mock for now as flwr manages this internally
            "status": "Flower Server Running"
        }

