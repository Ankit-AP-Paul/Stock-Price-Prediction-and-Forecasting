#!/usr/bin/env python3
"""
Comprehensive test of all image URL functionality
"""
import requests
import json
import time

def test_query(message, expected_message_type, should_have_image=True):
    """Test a query and check the response"""
    
    print(f"\n📝 Testing: {message}")
    print("-" * 40)
    
    url = "http://localhost:8000/chat"
    test_request = {"message": message}
    
    try:
        response = requests.post(url, json=test_request)
        
        if response.status_code == 200:
            data = response.json()
            message_type = data.get('message_type')
            image_url = data.get('image_url')
            
            print(f"📊 Message Type: {message_type}")
            print(f"🖼️  Image URL: {image_url}")
            
            # Check message type
            if message_type == expected_message_type:
                print(f"✅ Message type correct: {message_type}")
            else:
                print(f"❌ Message type wrong: expected {expected_message_type}, got {message_type}")
                return False
            
            # Check image URL
            if should_have_image:
                if image_url:
                    print(f"✅ Image URL returned: {image_url}")
                    return True
                else:
                    print("❌ Expected image URL but got None")
                    return False
            else:
                if not image_url:
                    print("✅ No image URL (as expected)")
                    return True
                else:
                    print(f"❌ Unexpected image URL: {image_url}")
                    return False
                    
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_comprehensive_tests():
    """Run comprehensive tests for all message types"""
    
    print("🧪 Comprehensive Image URL Test Suite")
    print("=" * 50)
    
    # Test cases: (message, expected_type, should_have_image)
    test_cases = [
        ("Should I buy WIPRO stock?", "investment_advice", True),
        ("Analyze TCS technical indicators", "stock_analysis", True), 
        ("Compare INFY vs WIPRO", "stock_comparison", True),
        ("How has ICICIBANK performed?", "performance_analysis", True),
        ("What is the current price of TCS?", "price_query", False),
        ("Tell me about the stock market", "general", False)
    ]
    
    results = []
    
    for message, expected_type, should_have_image in test_cases:
        result = test_query(message, expected_type, should_have_image)
        results.append(result)
        time.sleep(1)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Image URL functionality is working correctly!")
    else:
        print("💥 Some tests failed. Check the details above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_tests()
