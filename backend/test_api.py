import requests
import json

url = "https://b0z0h6knui.execute-api.us-east-1.amazonaws.com/"

payload = {
    "message": "I am a farmer. I did not receive PM-Kisan payment.",
    "language": "hi",
    "session_id": "demo-hackathon-123"
}

print("Sending request to API Gateway...")
response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
print("Response Text:")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)
