import requests
import json

response = requests.post("http://localhost:8001/chat", json={
    "message": "moving averages of SBIN",
    "session_id": "test_exact_query"
})

if response.status_code == 200:
    result = response.json()
    print("=== FINAL TEST RESULT ===")
    print(f"Message Type: {result.get('message_type')}")
    print(f"Image URL: {result.get('image_url')}")
    print(f"Status: {result.get('status')}")
    
    if result.get('message_type') == 'stock_analysis' and result.get('image_url'):
        print("\n🎉 SUCCESS: Moving averages query now correctly returns image URL!")
    else:
        print("\n❌ FAILED: Still not working correctly")
        
else:
    print(f"Error: {response.status_code}")
