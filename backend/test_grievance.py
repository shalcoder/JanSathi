import requests
import json

BASE_URL = "http://localhost:5010/v1/query"
HEADERS = {"Content-Type": "application/json", "Authorization": "Bearer mock_token"}
SESSION_ID = "test-grievance-session-1"

def send_msg(msg):
    res = requests.post(BASE_URL, json={"message": msg, "session_id": SESSION_ID, "language": "en"}, headers=HEADERS)
    print(json.dumps(res.json(), indent=2))

print("Testing Grievance flow:")
send_msg("My PM-Kisan payment has not arrived yet for January.")
send_msg("APP-123456")
send_msg("Lucknow")
send_msg("November 2024")
