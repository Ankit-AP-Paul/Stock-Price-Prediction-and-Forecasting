"""
Test script for Finance LLM Chatbot API endpoints with Indian companies
Run this to verify all API endpoints work correctly with Indian stocks
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
    """Test chat endpoint with Indian company questions"""
    print("\n💬 Testing chat endpoint with Indian companies...")
    
    test_questions = [
        "What is the current price of TCS?",
        "Can you analyze ICICI Bank for me?",
        "Should I invest in Reliance?",
        "Compare TCS and Infosys stocks",
        "How has SBI performed over the last 6 months?",
        "What are the moving averages of Wipro?",
        "Give me investment advice for HDFC Bank stock"
    ]
    
    for question in test_questions:
        print(f"\n📤 Asking: {question}")
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['status']}")
                print(f"📋 Type: {data['message_type']}")
                print(f"🤖 Response: {data['response'][:150]}...")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Chat test failed: {e}")

def test_stock_price():
    """Test stock price endpoint with Indian stocks"""
    print("\n📈 Testing stock price endpoint with Indian stocks...")
    
    indian_tickers = ["TCS", "INFY", "RELIANCE", "SBIN", "HDFCBANK", "WIPRO", "ICICIBANK"]
    
    for ticker in indian_tickers:
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
                print(f"🔄 Status: {data['status']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Stock price test failed for {ticker}: {e}")

def test_stock_analysis():
    """Test stock analysis endpoint with Indian stocks"""
    print("\n🔍 Testing stock analysis endpoint with Indian stocks...")
    
    test_stocks = [
        {"ticker": "ICICIBANK", "type": "basic"},
        {"ticker": "TCS", "type": "technical"},
        {"ticker": "RELIANCE", "type": "investment_advice"}
    ]
    
    for stock in test_stocks:
        print(f"\n🔍 Analyzing {stock['ticker']} ({stock['type']} analysis)...")
        try:
            response = requests.post(
                f"{BASE_URL}/stock/analysis",
                json={
                    "ticker": stock['ticker'],
                    "analysis_type": stock['type']
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analysis for {data['company_name']} ({data['ticker']})")
                analysis = data['analysis']
                
                # Print key analysis data
                if 'current_price' in analysis:
                    print(f"📊 Current Price: ₹{analysis['current_price']}")
                if 'change_percent' in analysis:
                    print(f"📈 Change: {analysis['change_percent']}%")
                if 'recommendation' in analysis:
                    print(f"💡 Recommendation: {analysis['recommendation']}")
                if 'technical_indicators' in analysis:
                    print(f"📊 Technical Indicators Available")
                    
                print(f"🔄 Status: {data['status']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Stock analysis test failed for {stock['ticker']}: {e}")

def test_stock_comparison():
    """Test stock comparison endpoint with Indian stocks"""
    print("\n⚖️ Testing stock comparison endpoint with Indian stocks...")
    
    comparisons = [
        ("TCS", "INFY"),
        ("RELIANCE", "HDFCBANK"),
        ("SBIN", "ICICIBANK")
    ]
    
    for ticker1, ticker2 in comparisons:
        print(f"\n⚖️ Comparing {ticker1} vs {ticker2}...")
        try:
            response = requests.post(
                f"{BASE_URL}/stock/compare",
                params={"ticker1": ticker1, "ticker2": ticker2},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Comparison: {data['company1_name']} vs {data['company2_name']}")
                comparison = data['comparison']
                
                # Print comparison data
                if 'current_price1' in comparison:
                    print(f"📊 {data['ticker1']} Price: ₹{comparison['current_price1']}")
                if 'current_price2' in comparison:
                    print(f"📊 {data['ticker2']} Price: ₹{comparison['current_price2']}")
                if 'performance_comparison' in comparison:
                    print(f"📈 Performance Comparison Available")
                if 'recommendation' in comparison:
                    print(f"💡 Recommendation: {comparison['recommendation']}")
                    
                print(f"🔄 Status: {data['status']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Stock comparison test failed for {ticker1} vs {ticker2}: {e}")

def test_root_endpoint():
    """Test root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info: {data['message']}")
            print(f"📋 Version: {data['version']}")
            print(f"🔗 Available Endpoints: {len(data['endpoints'])}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")

def main():
    """Run all tests with Indian companies"""
    print("🚀 Starting Finance LLM Chatbot API Tests with Indian Companies")
    print("=" * 60)
    
    # Test if server is running
    if not test_health():
        print("\n❌ API server is not running!")
        print("Please start the server with: python api.py")
        return
    
    # Run all tests
    test_root_endpoint()
    test_chat()
    test_stock_price()
    test_stock_analysis()
    test_stock_comparison()
    
    print("\n" + "=" * 60)
    print("✅ Indian Stock API testing completed!")
    print("\n📊 Tested Indian Companies:")
    print("• TCS (Tata Consultancy Services)")
    print("• INFY (Infosys)")
    print("• RELIANCE (Reliance Industries)")
    print("• SBIN (State Bank of India)")
    print("• HDFCBANK (HDFC Bank)")
    print("• WIPRO (Wipro)")
    print("• ICICIBANK (ICICI Bank)")
    
    print("\n🌐 Next steps for Next.js integration:")
    print("1. Copy the example component from nextjs-integration-example.tsx")
    print("2. Install required packages: npm install")
    print("3. Add the component to your Next.js app")
    print("4. Start your Next.js dev server: npm run dev")
    print(f"\n📚 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
