import requests
import json

# Test the moving averages detection fix
url = "http://localhost:8001/chat"
test_cases = [
    {
        "message": "Show me moving averages for SBIN",
        "description": "Moving averages query"
    },
    {
        "message": "What are the moving averages of TCS?",
        "description": "Moving averages query (alternative phrasing)"
    },
    {
        "message": "Give me technical analysis for RELIANCE",
        "description": "Technical analysis query"
    },
    {
        "message": "Show me RSI for INFY",
        "description": "RSI query"
    }
]

print("=== Testing Message Type Detection Fix ===\n")

for i, test_case in enumerate(test_cases, 1):
    print(f"Test {i}: {test_case['description']}")
    print(f"Query: '{test_case['message']}'")
    
    try:
        response = requests.post(url, json={
            "message": test_case["message"],
            "session_id": f"test_{i}"
        })
        
        if response.status_code == 200:
            result = response.json()
            message_type = result.get('message_type', 'None')
            image_url = result.get('image_url', 'None')
            
            print(f"✅ Message Type: {message_type}")
            print(f"✅ Image URL: {image_url}")
            
            # Check if it should have detected as stock_analysis
            if message_type == "stock_analysis" and image_url:
                print("🎉 SUCCESS: Correctly detected as stock analysis with image!")
            elif message_type == "stock_analysis":
                print("⚠️  PARTIAL: Detected as stock analysis but no image URL")
            else:
                print("❌ FAILED: Not detected as stock analysis")
                
        else:
            print(f"❌ ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("-" * 50)
