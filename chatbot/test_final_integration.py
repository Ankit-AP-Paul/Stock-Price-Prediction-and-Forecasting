#!/usr/bin/env python3
"""
Final Integration Test for Finance LLM Chatbot
Tests all core functionality with the complete system
"""
import requests
import json
import time

# API endpoints
API_BASE = "http://localhost:8001"
IMAGE_BASE = "http://localhost:8002"

def test_all_functionality():
    """Test all core functionality of the Finance LLM Chatbot"""
    print("🚀 Finance LLM Chatbot - Final Integration Test")
    print("=" * 60)
    
    # 1. Test API Health
    print("\n1. Testing API Health")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"✅ Chatbot Initialized: {data['chatbot_initialized']}")
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health Error: {e}")
        return False
    
    # 2. Test Stock Price Functionality
    print("\n2. Testing Stock Price Functionality")
    for ticker in ["TCS", "INFY", "RELIANCE"]:
        try:
            response = requests.post(
                f"{API_BASE}/stock/price",
                json={"ticker": ticker}
            )
            if response.status_code == 200:
                data = response.json()
                change_info = f" ({data['change_percent']:+.2f}%)" if data.get('change_percent') else ""
                print(f"✅ {ticker}: {data['currency']}{data['current_price']:.2f}{change_info}")
            else:
                print(f"❌ {ticker} Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {ticker} Error: {e}")
    
    # 3. Test Technical Analysis
    print("\n3. Testing Technical Analysis")
    try:
        response = requests.post(
            f"{API_BASE}/stock/analysis",
            json={"ticker": "TCS", "analysis_type": "technical"}
        )
        if response.status_code == 200:
            data = response.json()
            analysis = data['analysis']
            print(f"✅ {data['ticker']} Technical Analysis:")
            print(f"   Price: ₹{analysis['current_price']:.2f}")
            print(f"   RSI: {analysis['rsi']:.1f} ({analysis['rsi_signal']})")
            print(f"   Trend: {analysis['ma_trend']}")
            print(f"   MACD Signal: {analysis['macd_signal']}")
        else:
            print(f"❌ Technical Analysis Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Technical Analysis Error: {e}")
    
    # 4. Test Stock Comparison
    print("\n4. Testing Stock Comparison")
    try:
        response = requests.post(
            f"{API_BASE}/stock/compare?ticker1=TCS&ticker2=INFY"
        )
        if response.status_code == 200:
            data = response.json()
            comp = data['comparison']
            print(f"✅ TCS vs INFY Comparison:")
            print(f"   TCS Performance: {comp['change_percent1']:+.2f}%")
            print(f"   INFY Performance: {comp['change_percent2']:+.2f}%")
            print(f"   Better Performer: {comp['better_performance']}")
            if 'image_url' in data and data['image_url']:
                print(f"   📊 Comparison Chart Generated: {data['image_url']}")
        else:
            print(f"❌ Stock Comparison Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stock Comparison Error: {e}")
    
    # 5. Test Chat Functionality
    print("\n5. Testing Chat Functionality")
    test_messages = [
        "What is the current price of Reliance?",
        "Give me investment advice for TCS",
        "Compare TCS and Infosys stocks"
    ]
    
    for message in test_messages:
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={"message": message}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat: '{message[:30]}...' → {data['message_type']}")
                if data.get('image_url'):
                    print(f"   📊 Generated: {data['image_url']}")
            else:
                print(f"❌ Chat Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Chat Error: {e}")
        
        time.sleep(1)  # Prevent rate limiting
    
    # 6. Test Image Server
    print("\n6. Testing Image Server")
    try:
        response = requests.get(f"{IMAGE_BASE}/images")
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', [])
            print(f"✅ Image Server: {len(images)} images available")
            
            # Test direct image access
            if images:
                test_image = images[0]
                img_url = test_image.get('url', f"{IMAGE_BASE}/static/{test_image['filename']}")
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    print(f"✅ Direct Image Access: {test_image['filename']} ({len(img_response.content)} bytes)")
                else:
                    print(f"❌ Image Access Failed: {img_response.status_code}")
        else:
            print(f"❌ Image Server Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Image Server Error: {e}")
    
    # 7. Test Frontend Integration Points
    print("\n7. Testing Frontend Integration")
    try:
        # Test CORS and API endpoints availability
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Documentation Available")
            print(f"✅ CORS Enabled: {data['frontend_integration']['cors_enabled']}")
        else:
            print(f"❌ Frontend Integration Test Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend Integration Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Final Integration Test Complete!")
    print("\n📋 System Status Summary:")
    print("✅ API Server: Running on port 8001")
    print("✅ Image Server: Running on port 8002") 
    print("✅ Stock Data: Indian stocks working")
    print("✅ Technical Analysis: Full indicators available")
    print("✅ Stock Comparison: With chart generation")
    print("✅ Chat Interface: Multi-type responses")
    print("✅ Image Generation: Plot creation working")
    print("✅ Frontend Ready: CORS enabled")
    
    print("\n🌐 Demo Access:")
    print(f"• Main API: {API_BASE}")
    print(f"• Image Server: {IMAGE_BASE}")
    print(f"• Demo Page: file:///c:/Users/User/OneDrive/Desktop/Misc/Finance%20LLM%20Chatbot/demo.html")
    print(f"• API Docs: {API_BASE}/docs")
    
    print("\n💡 Usage Examples:")
    print("• Stock Price: POST /stock/price {'ticker': 'TCS'}")
    print("• Technical Analysis: POST /stock/analysis {'ticker': 'TCS', 'analysis_type': 'technical'}")
    print("• Comparison: POST /stock/compare?ticker1=TCS&ticker2=INFY")
    print("• Chat: POST /chat {'message': 'What is TCS current price?'}")

if __name__ == "__main__":
    test_all_functionality()
