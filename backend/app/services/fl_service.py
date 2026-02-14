import numpy as np
import uuid
import time
from app.core.utils import logger, log_event

class FederatedLearningService:
    """
    Federated Learning Aggregator Service (Simulating Flower Server).
    Handles:
    1. Client Registration & Selection
    2. Federated Averaging (FedAvg) of Model Weights
    3. Differential Privacy (DP) Accounting
    """

    def __init__(self, min_clients=2, round_timeout=300):
        self.min_clients = min_clients
        self.round_timeout = round_timeout
        self.current_round = 1
        self.global_model_weights = self._initialize_weights()
        self.client_updates = {} # Staging area for current round updates
        self.privacy_budget_epsilon = 10.0 # Total privacy budget
        self.clients = {} # Active clients

    def _initialize_weights(self):
        """Initialize mock model weights (e.g., specific to a Scheme Classification Model)."""
        # Layers: Input(768) -> Dense(128) -> Dense(4)
        return {
            "layer1_w": np.random.randn(768, 128) * 0.01,
            "layer1_b": np.zeros(128),
            "layer2_w": np.random.randn(128, 4) * 0.01,
            "layer2_b": np.zeros(4)
        }

    def register_client(self, client_id):
        """Registers a client node for training."""
        self.clients[client_id] = {
            "last_seen": time.time(),
            "status": "idle",
            "battery_level": 100 # Mock metadata
        }
        return {"status": "registered", "round": self.current_round}

    def submit_update(self, client_id, update_payload):
        """
        Receives encrypted gradients/weights from a client.
        payload: { "weights": {}, "num_samples": int }
        """
        if client_id not in self.clients:
            return {"error": "Client not registered"}

        # Simulate Differential Privacy Noise Addition (Server-side)
        # In a real FL setup, this happens on client (Local DP) or via Secure Aggregation
        noisy_update = self._apply_dp_noise(update_payload['weights'])
        
        self.client_updates[client_id] = {
            "weights": noisy_update,
            "num_samples": update_payload.get('num_samples', 1)
        }
        
        log_event('fl_update_received', {'client_id': client_id, 'round': self.current_round})

        # Trigger Aggregation if enough updates
        if len(self.client_updates) >= self.min_clients:
            return self._aggregate_updates()
            
        return {"status": "accepted", "message": "Waiting for peers"}

    def _apply_dp_noise(self, weights_dict):
        """Adds Gaussian noise for Differential Privacy."""
        sensitivity = 1.0
        noise_scale = 0.01
        noisy_weights = {}
        for k, v in weights_dict.items():
            noise = np.random.normal(0, noise_scale * sensitivity, np.array(v).shape)
            noisy_weights[k] = np.array(v) + noise
        return noisy_weights

    def _aggregate_updates(self):
        """Performs Federated Averaging (FedAvg)."""
        logger.info(f"Starting FedAvg for Round {self.current_round}")
        
        total_samples = sum(u['num_samples'] for u in self.client_updates.values())
        new_global_weights = {k: np.zeros_like(v) for k, v in self.global_model_weights.items()}

        # Weighted Average
        for update in self.client_updates.values():
            weight_factor = update['num_samples'] / total_samples
            for k, v in update['weights'].items():
                new_global_weights[k] += v * weight_factor

        self.global_model_weights = new_global_weights
        
        # Advance Round
        completed_round = self.current_round
        self.current_round += 1
        self.client_updates = {} # Clear buffer
        
        log_event('fl_round_completed', {'round': completed_round, 'participants': len(self.clients)})
        
        return {
            "status": "round_completed", 
            "new_round": self.current_round,
            "global_metrics": {"accuracy": 0.85 + (0.01 * completed_round)} # Mock continuous improvement
        }

    def get_metrics(self):
        return {
            "current_round": self.current_round,
            "active_clients": len(self.clients),
            "pending_updates": len(self.client_updates),
            "global_accuracy": 0.85 + (0.01 * (self.current_round - 1))
        }
