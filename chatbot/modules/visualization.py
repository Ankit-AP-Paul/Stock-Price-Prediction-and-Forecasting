import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

class Visualizer:
    """Helper class for creating finance-related visualizations"""
    
    @staticmethod
    def plot_stock(ticker, data, period="1y"):
        """
        Create and save a plot of the stock price
        
        Args:
            ticker (str): Stock ticker symbol
            data (pandas.DataFrame): Stock price data
            period (str): Time period displayed
            
        Returns:
            str: Path to the saved plot
        """
        if data is None or data.empty:
            return None
        
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data['Close'], label=f"{ticker} Close Price")
        
        # Add moving averages
        if 'MA50' not in data.columns:
            data['MA50'] = data['Close'].rolling(window=50).mean()
        if 'MA200' not in data.columns:
            data['MA200'] = data['Close'].rolling(window=200).mean()
            
        plt.plot(data.index, data['MA50'], label="50-day MA", alpha=0.7)
        plt.plot(data.index, data['MA200'], label="200-day MA", alpha=0.7)
        
        plt.title(f"{ticker} Stock Price ({period})")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save the plot directly to static directory
        import os
        static_dir = "static"
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        plot_path = os.path.join(static_dir, f"{ticker}_stock_plot.png")
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path
      # Portfolio composition visualization function removed as part of the removal of portfolio management functionality
      # Portfolio performance visualization function removed as part of the removal of portfolio management functionality
    
    @staticmethod
    def plot_stock_comparison(data1, data2, ticker1, ticker2, period="1y"):
        """
        Create a comparison plot of two stocks
        
        Args:
            data1 (pandas.DataFrame): First stock data
            data2 (pandas.DataFrame): Second stock data
            ticker1 (str): First ticker symbol
            ticker2 (str): Second ticker symbol
            period (str): Time period for the plot
            
        Returns:
            str: Path to saved plot file
        """
        if data1 is None or data1.empty or data2 is None or data2.empty:
            return None
        
        # Normalize data for comparison (starting value = 100)
        normalized1 = data1['Close'] / data1['Close'].iloc[0] * 100
        normalized2 = data2['Close'] / data2['Close'].iloc[0] * 100
        
        # Create plot
        plt.figure(figsize=(12, 6))
        plt.plot(normalized1.index, normalized1, label=ticker1)
        plt.plot(normalized2.index, normalized2, label=ticker2)
        plt.title(f"Comparison: {ticker1} vs {ticker2} ({period})")
        plt.xlabel("Date")
        plt.ylabel("Normalized Price (Start=100)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot directly to static directory
        import os
        static_dir = "static"
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        plot_path = os.path.join(static_dir, f"{ticker1}_vs_{ticker2}_comparison.png")
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path