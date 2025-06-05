import requests
import json

# Test the performance analysis endpoint
url = "http://localhost:8001/chat"
data = {
    "message": "How has TCS performed over the past 6 months?",
    "session_id": "test_image_url"
}

try:
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print("=== API Response ===")
        print(json.dumps(result, indent=2))
        print(f"\nImage URL: {result.get('image_url', 'None')}")
        print(f"Message Type: {result.get('message_type', 'None')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
