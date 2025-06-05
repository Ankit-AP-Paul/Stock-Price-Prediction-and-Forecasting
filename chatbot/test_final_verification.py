#!/usr/bin/env python3
"""
Final verification test for investment advice image URL fix
"""
import requests
import json
import os

def test_investment_advice_scenarios():
    """Test various investment advice scenarios"""
    
    print("🎯 Investment Advice Image URL Fix Verification")
    print("=" * 55)
    
    # Various investment advice queries
    investment_queries = [
        "Should I buy WIPRO stock?",
        "Is TCS a good investment?", 
        "Should I invest in ICICIBANK?",
        "Give me investment advice for INFY"
    ]
    
    url = "http://localhost:8000/chat"
    all_passed = True
    
    for i, query in enumerate(investment_queries, 1):
        print(f"\n🧪 Test {i}: {query}")
        print("-" * 40)
        
        try:
            response = requests.post(url, json={"message": query})
            
            if response.status_code == 200:
                data = response.json()
                message_type = data.get('message_type')
                image_url = data.get('image_url')
                
                print(f"📊 Message Type: {message_type}")
                print(f"🖼️  Image URL: {image_url}")
                
                # Check if investment advice was detected and image URL returned
                if message_type == "investment_advice" and image_url:
                    print("✅ SUCCESS: Investment advice with image URL!")
                elif message_type == "investment_advice" and not image_url:
                    print("❌ FAIL: Investment advice detected but no image URL")
                    all_passed = False
                else:
                    print(f"⚠️  INFO: Detected as '{message_type}' (not investment_advice)")
                    if image_url:
                        print("✅ But still got image URL, which is good!")
                    else:
                        print("❌ And no image URL returned")
                        all_passed = False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 55)
    print("🏁 FINAL VERIFICATION RESULTS")
    print("=" * 55)
    
    if all_passed:
        print("🎉 SUCCESS! Investment advice image URL fix is working!")
        print("✅ All investment advice queries returned proper image URLs")
    else:
        print("💥 Some investment advice queries failed to return image URLs")
    
    return all_passed

def check_static_folder():
    """Check what's in the static folder"""
    print("\n📁 Current Static Folder Contents:")
    static_files = os.listdir("static") if os.path.exists("static") else []
    
    png_files = [f for f in static_files if f.endswith('.png')]
    if png_files:
        for file in png_files:
            print(f"  📊 {file}")
    else:
        print("  ❌ No PNG files found")
    
    return png_files

if __name__ == "__main__":
    print("🚀 Starting Final Investment Advice Image URL Verification")
    
    # Check static folder first
    static_images = check_static_folder()
    
    # Run the tests
    success = test_investment_advice_scenarios()
    
    print(f"\n📈 Total images in static folder: {len(static_images)}")
    
    if success:
        print("\n🎯 MISSION ACCOMPLISHED!")
        print("The investment advice image URL fix is working correctly!")
    else:
        print("\n🔧 Still needs some adjustments")
        
    print("\n" + "=" * 55)
