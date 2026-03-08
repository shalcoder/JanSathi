import requests
import json
import time

BASE_URL = "http://localhost:5010/v1/query"
HEADERS = {"Content-Type": "application/json", "Authorization": "Bearer mock_token_for_testing"}

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"🚀 TESTING FEATURE: {title}")
    print(f"{'='*60}")

def send_msg(session_id, msg):
    print(f"\n🗣️ User says: \"{msg}\"")
    
    try:
        res = requests.post(
            BASE_URL, 
            json={"message": msg, "session_id": session_id, "language": "en"}, 
            headers=HEADERS
        )
        data = res.json()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend. Make sure it's running on port 5010!")
        return None

    # Print raw response to debug structure
    payload_str = json.dumps(data, indent=2)
    print(f"🤖 Agent Payload logged to file")
    with open("test_debug_output.txt", "a", encoding="utf-8") as f:
         f.write(f"\n🗣️ User says: \"{msg}\"\n")
         f.write(f"🤖 Agent Payload:\n{payload_str}\n")
    
    time.sleep(1) # Small pause for readability
    return data

def run_tests():
    # TEST 1: PM-Kisan Eligibility Validation
    print_separator("1. PM-Kisan Eligibility & Receipt Generation")
    session_1 = f"test-session-pmkisan-{int(time.time())}"
    send_msg(session_1, "I want to check my eligibility for PM Kisan.")
    send_msg(session_1, "Uttar Pradesh")
    send_msg(session_1, "1.5") # hectares
    send_msg(session_1, "150000") # income
    send_msg(session_1, "1234") # aadhaar last 4

    # TEST 2: PM Awas Yojana - Dynamic Gap Analysis
    print_separator("2. PM Awas Yojana - Dynamic Document Gap Analysis")
    session_2 = f"test-session-awas-{int(time.time())}"
    send_msg(session_2, "I want to apply for PM Awas Yojana.")
    send_msg(session_2, "Maharashtra") 
    send_msg(session_2, "100000") # family income
    send_msg(session_2, "kutcha") # housing status -> generates Self-declaration gap
    send_msg(session_2, "rural")  # rural -> generates Gram Panchayat NOC gap

    # TEST 3: Grievance Draft Generation Pipeline
    print_separator("3. PM-Kisan Grievance Generation & S3 Upload")
    session_3 = f"test-session-grievance-{int(time.time())}"
    send_msg(session_3, "My PM-Kisan payment has not arrived yet for January.")
    send_msg(session_3, "APP-987654") # Application ID
    send_msg(session_3, "Lucknow")      # District
    send_msg(session_3, "November 2024")# Last payment

    print("\n✅ All automated workflow tests completed!")

if __name__ == "__main__":
    run_tests()
