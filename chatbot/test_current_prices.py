#!/usr/bin/env python3
"""
Test the current price functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.stock_data import StockDataService

def test_current_prices():
    """Test current price functionality"""
    print("Testing Current Price Functionality")
    print("=" * 50)
    
    service = StockDataService()
    
    stocks = ["RELIANCE", "TCS", "ICICIBANK", "INFY"]
    
    for stock in stocks:
        print(f"\n{stock}:")
        price = service.get_current_price(stock)
        if price is not None:
            print(f"✓ Current price: ₹{price:.2f}")
        else:
            print("✗ Failed to get current price")

if __name__ == "__main__":
    test_current_prices()
