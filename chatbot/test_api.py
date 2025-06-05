"""
Test script for Finance LLM Chatbot API endpoints
Run this to verify all API endpoints are working correctly
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\n💬 Testing chat endpoint...")
      test_messages = [
        "What is the current price of TCS?",
        "Can you analyze ICICI Bank for me?",
        "Should I invest in Reliance?",
        "Compare TCS and Infosys stocks",
        "How has SBI performed over the last 6 months?",
        "What are the moving averages of Wipro?",
        "Give me investment advice for HDFC Bank stock"
    ]
    
    for message in test_messages:
        print(f"\n📤 Sending: {message}")
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['status']}")
                print(f"📋 Type: {data['message_type']}")
                print(f"🤖 Response: {data['response'][:100]}...")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Chat test failed: {e}")

def test_stock_price():
    """Test stock price endpoint"""
    print("\n📈 Testing stock price endpoint...")
    
    test_tickers = ["TCS", "INFY", "RELIANCE", "SBIN", "HDFCBANK"]
    
    for ticker in test_tickers:
        print(f"\n📊 Getting price for {ticker}...")
        try:
            response = requests.post(
                f"{BASE_URL}/stock/price",
                json={"ticker": ticker},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data['company_name']} ({data['ticker']})")
                print(f"💰 Price: {data['currency']}{data['current_price']:.2f}")
                if data.get('change_percent'):
                    print(f"📊 Change: {data['change_percent']:+.2f}%")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Stock price test failed: {e}")

def test_stock_analysis():
    """Test stock analysis endpoint"""
    print("\n🔍 Testing stock analysis endpoint...")
    
    try:        response = requests.post(
            f"{BASE_URL}/stock/analysis",
            json={
                "ticker": "ICICIBANK",
                "analysis_type": "basic"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis for {data['company_name']} ({data['ticker']})")
            print(f"📊 Current Price: ${data['analysis'].get('current_price', 'N/A')}")
            print(f"📈 Change: {data['analysis'].get('change_percent', 'N/A')}%")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Stock analysis test failed: {e}")

def test_stock_comparison():
    """Test stock comparison endpoint"""
    print("\n⚖️ Testing stock comparison endpoint...")
    
    try:        response = requests.post(
            f"{BASE_URL}/stock/compare",
            params={"ticker1": "TCS", "ticker2": "INFY"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Comparison: {data['company1_name']} vs {data['company2_name']}")
            comparison = data['comparison']
            print(f"📊 {data['ticker1']} Price: ${comparison.get('current_price1', 'N/A')}")
            print(f"📊 {data['ticker2']} Price: ${comparison.get('current_price2', 'N/A')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Stock comparison test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Finance LLM Chatbot API Tests")
    print("=" * 50)
    
    # Test if server is running
    if not test_health():
        print("\n❌ API server is not running!")
        print("Please start the server with: python api.py")
        return
    
    # Run all tests
    test_chat()
    test_stock_price()
    test_stock_analysis()
    test_stock_comparison()
    
    print("\n" + "=" * 50)
    print("✅ API testing completed!")
    print("\nNext steps for Next.js integration:")
    print("1. Copy the example component from nextjs-integration-example.tsx")
    print("2. Install required packages: npm install")
    print("3. Add the component to your Next.js app")
    print("4. Start your Next.js dev server: npm run dev")
    print("\nAPI Documentation available at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
