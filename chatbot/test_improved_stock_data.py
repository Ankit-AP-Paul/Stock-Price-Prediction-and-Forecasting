#!/usr/bin/env python3
"""
Test script to verify the improved stock data fetching functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.stock_data import StockDataService

def test_stock_data():
    """Test the improved stock data service"""
    print("Testing improved Stock Data Service")
    print("=" * 50)
    
    service = StockDataService()
    
    # Test with TCS
    print("\n1. Testing TCS stock data:")
    data = service.get_stock_data("TCS", period="5d")
    if data is not None:
        print(f"✓ Successfully retrieved TCS data with {len(data)} data points")
        print(f"✓ Latest close price: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("✗ Failed to retrieve TCS data")
    
    # Test with Reliance
    print("\n2. Testing RELIANCE stock data:")
    data = service.get_stock_data("RELIANCE", period="5d")
    if data is not None:
        print(f"✓ Successfully retrieved RELIANCE data with {len(data)} data points")
        print(f"✓ Latest close price: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("✗ Failed to retrieve RELIANCE data")
    
    # Test with Infosys
    print("\n3. Testing INFY stock data:")
    data = service.get_stock_data("INFY", period="5d")
    if data is not None:
        print(f"✓ Successfully retrieved INFY data with {len(data)} data points")
        print(f"✓ Latest close price: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("✗ Failed to retrieve INFY data")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_stock_data()
