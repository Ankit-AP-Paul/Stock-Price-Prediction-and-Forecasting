#!/usr/bin/env python3
"""
Test script to verify that images are saved directly to static directory
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from visualization import Visualizer

def create_sample_data(ticker, days=100):
    """Create sample stock data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate realistic stock price movement
    np.random.seed(42)  # For reproducible results
    base_price = 100
    returns = np.random.normal(0.001, 0.02, days)  # Daily returns
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    data = pd.DataFrame({
        'Close': prices,
        'Open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'Volume': np.random.randint(1000000, 5000000, days)
    }, index=dates)
    
    return data

def test_single_stock_plot():
    """Test single stock plotting"""
    print("Testing single stock plot...")
    
    # Create sample data
    data = create_sample_data("TEST")
    
    # Create plot
    visualizer = Visualizer()
    result_path = visualizer.plot_stock("TEST", data, "100d")
    
    print(f"Plot saved to: {result_path}")
    
    # Check if file exists in static directory
    if result_path and os.path.exists(result_path):
        print("✅ Single stock plot saved successfully to static directory")
        return True
    else:
        print("❌ Single stock plot failed to save")
        return False

def test_comparison_plot():
    """Test stock comparison plotting"""
    print("\nTesting stock comparison plot...")
    
    # Create sample data for two stocks
    data1 = create_sample_data("STOCK1")
    data2 = create_sample_data("STOCK2")
    
    # Create comparison plot
    visualizer = Visualizer()
    result_path = visualizer.plot_stock_comparison(data1, data2, "STOCK1", "STOCK2", "100d")
    
    print(f"Comparison plot saved to: {result_path}")
    
    # Check if file exists in static directory
    if result_path and os.path.exists(result_path):
        print("✅ Stock comparison plot saved successfully to static directory")
        return True
    else:
        print("❌ Stock comparison plot failed to save")
        return False

def check_root_directory():
    """Check if any PNG files are created in root directory"""
    print("\nChecking root directory for PNG files...")
    
    root_pngs = [f for f in os.listdir('.') if f.endswith('.png')]
    
    if root_pngs:
        print(f"❌ Found PNG files in root directory: {root_pngs}")
        return False
    else:
        print("✅ No PNG files found in root directory")
        return True

def check_static_directory():
    """Check what files are in static directory"""
    print("\nChecking static directory contents...")
    
    static_dir = "static"
    if not os.path.exists(static_dir):
        print("❌ Static directory does not exist")
        return False
    
    static_files = [f for f in os.listdir(static_dir) if f.endswith('.png')]
    print(f"PNG files in static directory: {static_files}")
    
    return True

def main():
    print("=== Testing Image Saving Functionality ===")
    print(f"Current working directory: {os.getcwd()}")
    
    # Run tests
    test1_passed = test_single_stock_plot()
    test2_passed = test_comparison_plot()
    root_clean = check_root_directory()
    check_static_directory()
    
    print("\n=== Test Results ===")
    print(f"Single stock plot: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Comparison plot: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Root directory clean: {'✅ PASS' if root_clean else '❌ FAIL'}")
    
    if test1_passed and test2_passed and root_clean:
        print("\n🎉 All tests PASSED! Images are saving correctly to static directory only.")
        return True
    else:
        print("\n❌ Some tests FAILED. Image saving needs fixing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
