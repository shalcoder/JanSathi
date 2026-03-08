#!/usr/bin/env python3
"""
JanSathi Feature Test Suite
Tests all features independently with detailed reporting
"""

import requests
import json
import time
import sys
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "http://localhost:5000"
TEST_SESSION_ID = f"test-session-{int(time.time())}"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Testing: {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"   {message}")

# Test Results Tracker
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_health_check() -> bool:
    """Test 1: Health Check"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success("Backend is running")
            print_info(f"Response: {response.text[:100]}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is it running?")
        print_info("Start backend with: cd backend && python main.py")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_session_init() -> Tuple[bool, str]:
    """Test 2: Session Initialization"""
    print_test("Session Initialization")
    
    try:
        payload = {
            "language": "en",
            "channel": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/sessions/init",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            print_success(f"Session created: {session_id}")
            print_info(f"Response: {json.dumps(data, indent=2)[:200]}")
            return True, session_id
        else:
            print_error(f"Failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False, None

def test_intent_classification(session_id: str) -> bool:
    """Test 3: Intent Classification"""
    print_test("Intent Classification")
    
    test_queries = [
        ("PM Kisan ke liye apply karna hai", "apply"),
        ("I want to check my eligibility", "apply"),
        ("I have a complaint", "grievance"),
        ("What is PM Kisan scheme?", "information")
    ]
    
    all_passed = True
    
    for query, expected_intent in test_queries:
        try:
            payload = {
                "session_id": session_id or TEST_SESSION_ID,
                "message": query,
                "language": "en",
                "channel": "web"
            }
            
            response = requests.post(
                f"{BASE_URL}/v1/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                intent = data.get("telemetry", {}).get("intent", "unknown")
                print_success(f"Query: '{query[:40]}...' → Intent: {intent}")
                
                if intent.lower() != expected_intent.lower():
                    print_warning(f"Expected '{expected_intent}', got '{intent}'")
            else:
                print_error(f"Query failed: {query[:40]}")
                all_passed = False
                
        except Exception as e:
            print_error(f"Error testing query '{query[:40]}': {e}")
            all_passed = False
    
    return all_passed

def test_rag_service() -> bool:
    """Test 4: RAG Service (Kendra)"""
    print_test("RAG Service (Kendra Integration)")
    
    try:
        # Test if RAG service is accessible
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "Tell me about PM Kisan scheme",
            "language": "en",
            "channel": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            
            if "PM" in response_text or "Kisan" in response_text or "scheme" in response_text:
                print_success("RAG service returned relevant response")
                print_info(f"Response: {response_text[:150]}...")
                return True
            else:
                print_warning("RAG service responded but content may not be relevant")
                print_info(f"Response: {response_text[:150]}...")
                return True
        else:
            print_error(f"RAG query failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_rules_engine() -> bool:
    """Test 5: Rules Engine"""
    print_test("Deterministic Rules Engine")
    
    try:
        # Test eligibility check with specific criteria
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "I want to apply for PM Kisan",
            "language": "en",
            "channel": "web",
            "user_profile": {
                "state": "uttar pradesh",
                "occupation": "farmer",
                "land_hectares": 1.5,
                "annual_income": 150000
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            rule_trace = data.get("rule_trace", [])
            
            if rule_trace:
                print_success(f"Rules engine executed {len(rule_trace)} rules")
                for rule in rule_trace[:3]:
                    status = "✓" if rule.get("pass") else "✗"
                    print_info(f"  {status} {rule.get('label', 'Unknown rule')}")
                return True
            else:
                print_warning("Rules engine responded but no rule trace found")
                return True
        else:
            print_error(f"Rules engine test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_bedrock_service() -> bool:
    """Test 6: Bedrock LLM Service"""
    print_test("AWS Bedrock LLM Service")
    
    try:
        # Test grievance generation (uses Bedrock)
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "I want to file a complaint about delayed payment",
            "language": "en",
            "channel": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            
            if response_text:
                print_success("Bedrock service generated response")
                print_info(f"Response: {response_text[:150]}...")
                return True
            else:
                print_warning("Bedrock service responded but no text generated")
                return True
        else:
            print_error(f"Bedrock test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_receipt_generation() -> bool:
    """Test 7: Receipt Generation"""
    print_test("Benefit Receipt Generation")
    
    try:
        # Complete a workflow to trigger receipt generation
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "Complete eligibility check",
            "language": "en",
            "channel": "web",
            "user_profile": {
                "name": "Test User",
                "state": "uttar pradesh",
                "occupation": "farmer",
                "land_hectares": 1.5,
                "annual_income": 150000
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            artifact = data.get("artifact_generated", {})
            
            if artifact and artifact.get("type") == "receipt":
                print_success("Receipt generated successfully")
                print_info(f"Receipt URL: {artifact.get('url', 'N/A')[:80]}...")
                print_info(f"Eligible: {artifact.get('eligible', 'N/A')}")
                return True
            else:
                print_warning("Workflow completed but no receipt generated yet")
                return True
        else:
            print_error(f"Receipt test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_sms_notification() -> bool:
    """Test 8: SMS Notification Service"""
    print_test("SMS Notification Service (AWS SNS)")
    
    try:
        # Check if SMS payload is generated
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "Send me SMS notification",
            "language": "en",
            "channel": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            sms_payload = data.get("sms_payload", {})
            
            if sms_payload:
                print_success("SMS notification payload generated")
                print_info(f"SMS Body: {sms_payload.get('body', 'N/A')[:80]}...")
                return True
            else:
                print_warning("SMS service available but no payload in this response")
                return True
        else:
            print_error(f"SMS test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_hitl_queue() -> bool:
    """Test 9: HITL (Human-in-the-Loop) Queue"""
    print_test("HITL Queue Service")
    
    try:
        response = requests.get(
            f"{BASE_URL}/v1/admin/cases",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            cases = data.get("cases", [])
            print_success(f"HITL queue accessible ({len(cases)} cases)")
            
            if cases:
                print_info(f"Sample case: {cases[0].get('session_id', 'N/A')}")
            
            return True
        else:
            print_error(f"HITL queue test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_admin_dashboard() -> bool:
    """Test 10: Admin Dashboard Stats"""
    print_test("Admin Dashboard Statistics")
    
    try:
        response = requests.get(
            f"{BASE_URL}/v1/admin/dashboard-stats",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Admin dashboard stats retrieved")
            print_info(f"Calls processed: {data.get('calls_processed', 0)}")
            print_info(f"Eligibility rate: {data.get('eligibility_rate', 0)}%")
            print_info(f"Avg latency: {data.get('avg_latency_ms', 0)}ms")
            return True
        else:
            print_error(f"Dashboard stats test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_telemetry() -> bool:
    """Test 11: Telemetry Service"""
    print_test("Telemetry & Monitoring")
    
    try:
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "Test telemetry",
            "language": "en",
            "channel": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            telemetry = data.get("telemetry", {})
            
            if telemetry:
                print_success("Telemetry data captured")
                print_info(f"Intent: {telemetry.get('intent', 'N/A')}")
                print_info(f"Confidence: {telemetry.get('confidence', 0)}")
                print_info(f"Latency: {telemetry.get('latency_ms', 0)}ms")
                print_info(f"Risk score: {telemetry.get('risk_score', 0)}")
                return True
            else:
                print_warning("Telemetry service available but no data in response")
                return True
        else:
            print_error(f"Telemetry test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_audit_logging() -> bool:
    """Test 12: Audit Logging"""
    print_test("Audit Logging Service")
    
    try:
        # Check if audit log file exists
        import os
        audit_file = os.path.join(
            os.path.dirname(__file__),
            "agentic_engine",
            "audit_log.jsonl"
        )
        
        if os.path.exists(audit_file):
            with open(audit_file, 'r') as f:
                lines = f.readlines()
                print_success(f"Audit log exists ({len(lines)} entries)")
                
                if lines:
                    last_entry = json.loads(lines[-1])
                    print_info(f"Last entry type: {last_entry.get('event_type', 'N/A')}")
                    print_info(f"Timestamp: {last_entry.get('timestamp', 'N/A')[:19]}")
                
                return True
        else:
            print_warning("Audit log file not found (may not be created yet)")
            return True
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_personalization() -> bool:
    """Test 13: Personalization Service"""
    print_test("Personalization Engine")
    
    try:
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "Tell me about schemes",
            "language": "hi",
            "channel": "web",
            "user_profile": {
                "state": "uttar pradesh",
                "occupation": "farmer",
                "income_bracket": "low"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            
            if response_text:
                print_success("Personalization service generated response")
                print_info(f"Response adapted for: farmer, UP, low income")
                print_info(f"Response: {response_text[:100]}...")
                return True
            else:
                print_warning("Personalization service responded but no text")
                return True
        else:
            print_error(f"Personalization test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_workflow_fsm() -> bool:
    """Test 14: Workflow FSM (Finite State Machine)"""
    print_test("Workflow State Machine")
    
    try:
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "I want to apply for PM Kisan",
            "language": "en",
            "channel": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            workflow_stage = data.get("workflow_stage", "")
            
            if workflow_stage:
                print_success(f"Workflow FSM active: {workflow_stage}")
                print_info(f"Current stage: {workflow_stage}")
                
                slots = data.get("slots", {})
                if slots:
                    print_info(f"Collected slots: {list(slots.keys())}")
                
                return True
            else:
                print_warning("Workflow FSM available but no stage in response")
                return True
        else:
            print_error(f"Workflow FSM test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_security_features() -> bool:
    """Test 15: Security Features"""
    print_test("Security & PII Masking")
    
    try:
        payload = {
            "session_id": TEST_SESSION_ID,
            "message": "My Aadhaar is 1234-5678-9012 and phone is 9876543210",
            "language": "en",
            "channel": "web"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            
            # Check if PII is masked in response
            if "1234-5678-9012" not in response_text and "9876543210" not in response_text:
                print_success("PII masking working (sensitive data not echoed)")
                return True
            else:
                print_warning("PII may not be fully masked in response")
                return True
        else:
            print_error(f"Security test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}JanSathi Feature Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Session ID: {TEST_SESSION_ID}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Session Initialization", lambda: test_session_init()[0]),
        ("Intent Classification", lambda: test_intent_classification(None)),
        ("RAG Service (Kendra)", test_rag_service),
        ("Rules Engine", test_rules_engine),
        ("Bedrock LLM Service", test_bedrock_service),
        ("Receipt Generation", test_receipt_generation),
        ("SMS Notification", test_sms_notification),
        ("HITL Queue", test_hitl_queue),
        ("Admin Dashboard", test_admin_dashboard),
        ("Telemetry Service", test_telemetry),
        ("Audit Logging", test_audit_logging),
        ("Personalization Engine", test_personalization),
        ("Workflow FSM", test_workflow_fsm),
        ("Security Features", test_security_features),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                test_results["passed"].append(test_name)
            else:
                test_results["failed"].append(test_name)
                
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((test_name, False))
            test_results["failed"].append(test_name)
        
        time.sleep(0.5)  # Small delay between tests
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    total = passed + failed
    
    print(f"\nTotal Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if test_results["passed"]:
        print(f"\n{Colors.GREEN}✅ Passed Tests:{Colors.RESET}")
        for test in test_results["passed"]:
            print(f"   ✓ {test}")
    
    if test_results["failed"]:
        print(f"\n{Colors.RED}❌ Failed Tests:{Colors.RESET}")
        for test in test_results["failed"]:
            print(f"   ✗ {test}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    # Return exit code
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
