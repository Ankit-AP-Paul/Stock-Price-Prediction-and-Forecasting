#!/usr/bin/env python3
"""
Complete integration test for Finance LLM Chatbot
Tests both API server (8001) and Image server (8002)
"""
import requests
import json
import time
import os

# API endpoints
API_BASE = "http://localhost:8001"
IMAGE_BASE = "http://localhost:8002"

def test_api_health():
    """Test main API health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ API Health: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Health failed: {e}")
        return False

def test_image_server_health():
    """Test image server health"""
    try:
        response = requests.get(f"{IMAGE_BASE}/images")
        print(f"✅ Image Server: {response.status_code} - Available images: {len(response.json())}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Image Server failed: {e}")
        return False

def test_chat_with_plot_generation():
    """Test chat endpoint that should generate plots"""
    test_messages = [
        "Compare TCS vs INFY stock performance",
        "Show me technical analysis for RELIANCE",
        "What's the 6-month performance of SBIN?"
    ]
    
    for message in test_messages:
        print(f"\n🔍 Testing: {message}")
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={"message": message}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat Response: {data['response'][:100]}...")
                if 'image_url' in data and data['image_url']:
                    print(f"📊 Generated image: {data['image_url']}")
                else:
                    print("ℹ️  No image generated")
            else:
                print(f"❌ Chat failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Chat error: {e}")
        
        time.sleep(2)  # Wait between requests

def test_stock_price():
    """Test stock price endpoint"""
    stocks = ["TCS", "INFY", "RELIANCE"]
    
    for stock in stocks:
        try:
            response = requests.post(
                f"{API_BASE}/stock/price",
                json={"ticker": stock}
            )
            if response.status_code == 200:
                data = response.json()
                change_info = f" ({data['change_percent']:+.2f}%)" if data.get('change_percent') else ""
                print(f"✅ {stock}: {data['currency']}{data['current_price']}{change_info}")
            else:
                print(f"❌ {stock} price failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ {stock} price error: {e}")

def test_stock_comparison():
    """Test stock comparison endpoint"""
    comparisons = [("TCS", "INFY"), ("RELIANCE", "HDFCBANK")]
    
    for stock1, stock2 in comparisons:
        try:
            response = requests.post(
                f"{API_BASE}/stock/compare?ticker1={stock1}&ticker2={stock2}"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {stock1} vs {stock2}: Comparison successful")
                if 'image_url' in data and data['image_url']:
                    print(f"📊 Comparison chart: {data['image_url']}")
                else:
                    print("ℹ️  No comparison chart generated")
            else:
                print(f"❌ {stock1} vs {stock2} comparison failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ {stock1} vs {stock2} comparison error: {e}")

def test_latest_images():
    """Test getting latest generated images"""
    try:
        response = requests.get(f"{IMAGE_BASE}/images")
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', data)  # Handle both formats
            print(f"✅ Latest images: {len(images)} found")
            for i, img in enumerate(images[:3]):  # Show first 3
                if isinstance(img, dict):
                    filename = img.get('filename', f'image_{i}')
                    img_type = img.get('type', 'unknown')
                    print(f"  📊 {filename} - {img_type}")
                else:
                    print(f"  📊 {img}")
        else:
            print(f"❌ Latest images failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Latest images error: {e}")

def test_direct_image_access():
    """Test direct access to plot images"""
    try:
        # Check what images are available
        response = requests.get(f"{IMAGE_BASE}/images")
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', data)  # Handle both formats
            if images and len(images) > 0:
                # Try to access the first image directly
                first_image = images[0]
                if isinstance(first_image, dict):
                    filename = first_image.get('filename', '')
                    img_url = first_image.get('url', f"{IMAGE_BASE}/static/{filename}")
                else:
                    filename = str(first_image)
                    img_url = f"{IMAGE_BASE}/static/{filename}"
                
                if filename:
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        print(f"✅ Direct image access works: {filename}")
                        print(f"   Image size: {len(img_response.content)} bytes")
                    else:
                        print(f"❌ Direct image access failed: {img_response.status_code}")
                else:
                    print("❌ No valid filename found")
            else:
                print("ℹ️  No images available for direct access test")
    except Exception as e:
        print(f"❌ Direct image access error: {e}")

def main():
    print("🚀 Finance LLM Chatbot - Complete Integration Test")
    print("=" * 60)
    
    # Test basic connectivity
    print("\n1. Testing API Connectivity")
    api_ok = test_api_health()
    image_ok = test_image_server_health()
    
    if not api_ok or not image_ok:
        print("❌ Basic connectivity failed. Make sure both servers are running.")
        return
    
    # Test stock price functionality
    print("\n2. Testing Stock Price Endpoint")
    test_stock_price()
    
    # Test stock comparison (should generate plots)
    print("\n3. Testing Stock Comparison (Plot Generation)")
    test_stock_comparison()
    
    # Test chat with plot generation
    print("\n4. Testing Chat with Plot Generation")
    test_chat_with_plot_generation()
    
    # Wait a bit for plots to be generated
    print("\n5. Waiting for plot generation...")
    time.sleep(5)
    
    # Test image server functionality
    print("\n6. Testing Image Server")
    test_latest_images()
    test_direct_image_access()
    
    print("\n✅ Integration testing complete!")
    print("\n📋 Next steps:")
    print("1. Open demo.html in your browser")
    print("2. Test the chat interface")
    print("3. Check that images appear in the gallery")
    print(f"4. Main API: {API_BASE}")
    print(f"5. Image Server: {IMAGE_BASE}")

if __name__ == "__main__":
    main()
