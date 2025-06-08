#!/usr/bin/env python3
"""
Test investment advice image URL fix
"""
import requests
import json

def test_investment_advice_image_fix():
    """Test that investment advice requests return proper image URLs"""
    
    print("🧪 Testing Investment Advice Image URL Fix")
    print("=" * 50)
    
    # Test URL
    url = "http://localhost:8000/chat"
    
    # Test investment advice request
    test_request = {
        "message": "Should I buy WIPRO stock?"
    }
    
    print(f"📝 Sending request: {test_request['message']}")
    
    try:
        response = requests.post(url, json=test_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received successfully")
            print(f"📊 Message Type: {data.get('message_type', 'N/A')}")
            print(f"🖼️  Image URL: {data.get('image_url', 'None')}")
            print(f"💬 Response Preview: {data.get('response', '')[:100]}...")
            
            # Check if image URL is properly returned
            if data.get('message_type') == 'investment_advice' and data.get('image_url'):
                print("✅ SUCCESS: Investment advice returned with image URL!")
                return True
            elif data.get('message_type') == 'investment_advice' and not data.get('image_url'):
                print("❌ ISSUE: Investment advice detected but no image URL returned")
                return False
            else:
                print(f"❌ ISSUE: Message type was '{data.get('message_type')}' instead of 'investment_advice'")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: API server not running")
        print("💡 Start the API server with: python -m uvicorn api:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_static_images():
    """Check what images are currently in the static folder"""
    import os
    import glob
    
    print("\n📁 Current images in static folder:")
    static_pattern = "static/*.png"
    images = glob.glob(static_pattern)
    
    if images:
        for img in images:
            print(f"  - {img}")
    else:
        print("  - No images found")
    
    return images

if __name__ == "__main__":
    print("🚀 Starting Investment Advice Image Fix Test")
    
    # Check current images
    static_images = check_static_images()
    
    # Test the fix
    success = test_investment_advice_image_fix()
    
    if success:
        print("\n🎉 Investment advice image URL fix is working!")
    else:
        print("\n💥 Investment advice image URL fix needs more work")
        
    print("\n" + "=" * 50)
