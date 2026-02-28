import requests
import json

def test_integration():
    print("--- STEP 5: LIVE ENDPOINT TEST ---")
    url = "http://localhost:5000/agent/execute"
    payload = {
        "user_id": "demo",
        "channel": "web",
        "input_type": "text",
        "message": "Am I eligible for PM Kisan?"
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
        if r.status_code == 200:
            intent = r.json().get("intent")
            if intent == "ELIGIBILITY":
                print("✅ Agent Endpoint: PASS")
            else:
                print(f"❌ Agent Endpoint: FAIL (Unexpected intent: {intent})")
        else:
            print("❌ Agent Endpoint: FAIL")
    except Exception as e:
        print(f"❌ Agent Endpoint Error: {e}")

    print("\n--- STEP 6: REGRESSION TEST ---")
    # Health check
    try:
        r = requests.get("http://localhost:5000/health")
        print(f"Health Status: {r.status_code}")
        # print(f"Health Response: {r.text[:100]}...")
        if r.status_code == 200:
            print("✅ Health Endpoint: PASS")
        else:
            print("❌ Health Endpoint: FAIL")
    except Exception as e:
        print(f"❌ Health Endpoint Error: {e}")

    # Query endpoint
    try:
        url = "http://localhost:5000/query"
        payload = {"text_query": "What is PM Kisan?", "language": "en"}
        r = requests.post(url, json=payload)
        print(f"Query Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Query Endpoint: PASS")
        else:
            print(f"❌ Query Endpoint: FAIL (Status {r.status_code})")
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"❌ Query Endpoint Error: {e}")

if __name__ == "__main__":
    test_integration()
