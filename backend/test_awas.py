import requests
import json

BASE_URL = "http://localhost:5010/v1/query"
HEADERS = {"Content-Type": "application/json", "Authorization": "Bearer mock_token"}
SESSION_ID = "test-awas-session-3"

def send_msg(msg):
    print(f"\nUser: {msg}")
    res = requests.post(BASE_URL, json={"message": msg, "session_id": SESSION_ID, "language": "en"}, headers=HEADERS)
    data = res.json()
    print(f"Agent Payload: {json.dumps(data, indent=2)}")
    return data

send_msg("I want to apply for PM Awas Yojana.")
send_msg("Uttar Pradesh")
send_msg("100000")
send_msg("kutcha")
send_msg("rural")
