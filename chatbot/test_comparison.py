#!/usr/bin/env python3
"""
Test script to verify stock comparison functionality
Tests if we're getting 1-year historical data instead of intraday data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finance_chatbot import FinanceChatbot
from modules.stock_data import StockDataService

def test_stock_comparison():
    """Test the stock comparison functionality"""
    print("Testing Stock Comparison Functionality")
    print("=" * 50)
    
    # Initialize the chatbot
    chatbot = FinanceChatbot()
    
    # Test comparison query
    test_query = "Compare RELIANCE and TCS stocks"
    print(f"Query: {test_query}")
    print("-" * 30)
    
    # Get the response
    response = chatbot.get_response(test_query)
    print(response)
    
    print("\n" + "=" * 50)
    print("Testing Raw Data Retrieval")
    print("=" * 50)
    
    # Test raw data retrieval to see how much data we're getting
    stock_service = StockDataService()
    
    for ticker in ['RELIANCE', 'TCS']:
        print(f"\nTesting {ticker} with 1-year period:")
        data = stock_service.get_stock_data(ticker, period="1y")
        if data is not None and not data.empty:
            print(f"✓ Retrieved {len(data)} data points")
            print(f"  Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"  Sample prices:")
            print(f"    First: ₹{data['Close'].iloc[0]:.2f} ({data.index[0].strftime('%Y-%m-%d')})")
            print(f"    Last: ₹{data['Close'].iloc[-1]:.2f} ({data.index[-1].strftime('%Y-%m-%d')})")
            if len(data) > 100:
                print(f"    Mid-point: ₹{data['Close'].iloc[len(data)//2]:.2f} ({data.index[len(data)//2].strftime('%Y-%m-%d')})")
        else:
            print(f"✗ No data retrieved for {ticker}")

if __name__ == "__main__":
    test_stock_comparison()
