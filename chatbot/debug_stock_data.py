#!/usr/bin/env python3
"""
Debug script to check what's happening with the stock data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.stock_data import StockDataService
import pandas as pd

def debug_stock_data():
    """Debug the stock data to see why we're getting NaN values"""
    print("Debugging Stock Data Issues")
    print("=" * 50)
    
    service = StockDataService()
    
    # Test with RELIANCE
    print("\n1. Debugging RELIANCE stock data:")
    data = service.get_stock_data("RELIANCE", period="5d")
    
    if data is not None:
        print(f"Data shape: {data.shape}")
        print(f"Columns: {list(data.columns)}")
        print(f"Index type: {type(data.index)}")
        print(f"Data types:\n{data.dtypes}")
        print(f"\nFirst few rows:")
        print(data.head())
        print(f"\nLast few rows:")
        print(data.tail())
        print(f"\nClose column info:")
        print(f"Close column type: {type(data['Close'])}")
        print(f"Close values: {data['Close'].values}")
        print(f"Last close value: {data['Close'].iloc[-1]}")
        print(f"Last close value type: {type(data['Close'].iloc[-1])}")
        
        # Check for NaN values
        print(f"\nNaN values in Close column: {data['Close'].isna().sum()}")
        print(f"Non-null values in Close column: {data['Close'].count()}")
        
        # Try to get a valid price
        valid_prices = data['Close'].dropna()
        if not valid_prices.empty:
            print(f"Last valid close price: {valid_prices.iloc[-1]}")
        else:
            print("No valid close prices found!")
    else:
        print("✗ Failed to retrieve RELIANCE data")

if __name__ == "__main__":
    debug_stock_data()
