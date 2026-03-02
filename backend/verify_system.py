import os
import sys
import unittest
import time
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agentic_engine.session_manager import SessionManager
from agentic_engine.storage import LocalJSONStorage
from app.services.rules_engine import RulesEngine
from app.tasks.verification_tasks import aadhaar_verify, bank_verify
from app.tasks.engine_tasks import evaluate_eligibility

class TestPhase3Logic(unittest.TestCase):
    def setUp(self):
        # Use a temporary session file for testing
        self.test_session_file = "backend/agentic_engine/test_sessions.json"
        self.storage = LocalJSONStorage(self.test_session_file)
        self.sm = SessionManager(self.storage)
        self.session_id = f"test-sess-{int(time.time())}"

    def tearDown(self):
        if os.path.exists(self.test_session_file):
            os.remove(self.test_session_file)

    def test_session_persistence_logic(self):
        """Verify the new per-session storage logic in SessionManager."""
        print("Testing SessionManager per-session storage...")
        self.sm.create_session(self.session_id)
        self.sm.update_data(self.session_id, "test_key", "test_value")
        
        # Verify it's saved in storage
        session = self.storage.get_session(self.session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session["data"]["test_key"], "test_value")
        self.assertIn("created_at", session)

    def test_rules_engine_deterministic(self):
        """Verify the RulesEngine evaluates eligibility correctly."""
        print("Testing RulesEngine evaluation...")
        engine = RulesEngine()
        user_profile = {"land_hectares": 1.5, "annual_income": 150000}
        rules = {
            "mandatory": [
                {"field": "land_hectares", "operator": "lte", "value": 2.0, "label": "Land < 2ha"},
                {"field": "annual_income", "operator": "lte", "value": 200000, "label": "Income < 2L"}
            ]
        }
        eligible, breakdown, score = engine.evaluate(user_profile, rules)
        self.assertTrue(eligible)
        self.assertEqual(score, 1.0)
        self.assertTrue(breakdown[0]["pass"])

    def test_step_function_handlers(self):
        """Verify the Lambda handlers for Step Functions."""
        print("Testing Step Function Lambda handlers...")
        # Test Aadhaar Verify
        res = aadhaar_verify({"id_number": "123456789012"}, None)
        self.assertEqual(res["status"], "verified")
        
        # Test Bank Verify
        res = bank_verify({"phone": "9876543210"}, None)
        self.assertEqual(res["status"], "active")

if __name__ == "__main__":
    unittest.main()
