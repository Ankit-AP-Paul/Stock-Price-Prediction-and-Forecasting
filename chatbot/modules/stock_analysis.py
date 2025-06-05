import numpy as np
import pandas as pd
from modules.stock_data import StockDataService
from modules.visualization import Visualizer

class StockAnalyzer:
    """Analyzer for stock data and technical indicators"""
    
    def __init__(self):
        """Initialize the stock analyzer"""
        self.stock_data_service = StockDataService()
    
    def analyze_stock(self, ticker):
        """
        Perform basic analysis of a stock
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            dict: Analysis results
        """
        data = self.stock_data_service.get_stock_data(ticker)
        if data is None or data.empty:
            return {"error": f"Could not retrieve data for {ticker}"}
        
        # Calculate some basic metrics
        current_price = data['Close'].iloc[-1]
        start_price = data['Close'].iloc[0]
        change_pct = ((current_price - start_price) / start_price) * 100
        
        # Ensure moving averages are calculated
        if 'MA50' not in data.columns:
            data['MA50'] = data['Close'].rolling(window=50).mean()
        if 'MA200' not in data.columns:
            data['MA200'] = data['Close'].rolling(window=200).mean()
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Simple trend analysis
        if data['MA50'].iloc[-1] > data['MA200'].iloc[-1]:
            trend = "Bullish (50-day MA above 200-day MA)"
        else:
            trend = "Bearish (50-day MA below 200-day MA)"
        
        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "change_percent": round(change_pct, 2),
            "volume": round(data['Volume'].mean()),
            "trend": trend,
            "rsi": round(current_rsi, 2),
            "data": data
        }
    
    def plot_stock(self, ticker, period="1y"):
        """
        Create and save a plot of the stock price
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period to retrieve data for
            
        Returns:
            str: Path to the saved plot
        """
        print(f"Plotting stock {ticker} for period: {period}")
        data = self.stock_data_service.get_stock_data(ticker, period)
        if data is None or data.empty:
            return None
        
        return Visualizer.plot_stock(ticker, data, period)
    
    def get_technical_analysis(self, ticker):
        """
        Get full technical analysis for a stock
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            dict: Technical analysis results
        """
        data = self.stock_data_service.get_stock_data(ticker)
        if data is None or data.empty:
            return {"error": f"Could not retrieve data for {ticker}"}
        
        # Ensure moving averages are calculated
        if 'MA50' not in data.columns:
            data['MA50'] = data['Close'].rolling(window=50).mean()
        if 'MA200' not in data.columns:
            data['MA200'] = data['Close'].rolling(window=200).mean()
        
        # Current values
        current_price = data['Close'].iloc[-1]
        ma50 = data['MA50'].iloc[-1]
        ma200 = data['MA200'].iloc[-1]
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Calculate MACD
        exp12 = data['Close'].ewm(span=12, adjust=False).mean()
        exp26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        
        # Calculate Bollinger Bands
        std20 = data['Close'].rolling(window=20).std()
        upper_band = data['MA50'] + (std20 * 2)
        lower_band = data['MA50'] - (std20 * 2)
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
          # Determine trend and signals
        price_vs_ma50 = "Price is above 50-day MA" if current_price > ma50 else "Price is below 50-day MA"
        price_vs_ma200 = "Price is above 200-day MA" if current_price > ma200 else "Price is below 200-day MA"
        ma_trend = "Bullish" if ma50 > ma200 else "Bearish"
        
        macd_signal = "Bullish" if current_macd > current_signal else "Bearish"
        rsi_signal = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
        
        bollinger_signal = "None"
        if current_price > current_upper:
            bollinger_signal = "Overbought"
        elif current_price < current_lower:
            bollinger_signal = "Oversold"
            
        return {
            "ticker": ticker,
            "current_price": current_price,
            "ma50": ma50,
            "ma200": ma200,
            "rsi": current_rsi,
            "macd": current_macd,
            "macd_signal": current_signal,
            "upper_band": current_upper,
            "lower_band": current_lower,
            "price_vs_ma50": price_vs_ma50,
            "price_vs_ma200": price_vs_ma200,
            "ma_trend": ma_trend,
            "macd_trend": macd_signal,
            "rsi_signal": rsi_signal,
            "bollinger_signal": bollinger_signal
        }
    
    def get_stock_comparison(self, ticker1, ticker2, period="1y"):
        """
        Compare two stocks over a given period
        
        Args:
            ticker1 (str): First stock ticker symbol
            ticker2 (str): Second stock ticker symbol
            period (str): Time period for comparison
            
        Returns:
            dict: Comparison results
        """
        # Get data for both stocks
        data1 = self.stock_data_service.get_stock_data(ticker1, period)
        data2 = self.stock_data_service.get_stock_data(ticker2, period)
        
        if data1 is None or data1.empty:
            return {"error": f"Could not retrieve data for {ticker1}"}
        
        if data2 is None or data2.empty:
            return {"error": f"Could not retrieve data for {ticker2}"}
        
        # Calculate key metrics for company 1
        current_price1 = data1['Close'].iloc[-1]
        start_price1 = data1['Close'].iloc[0]
        change_pct1 = ((current_price1 - start_price1) / start_price1) * 100
        
        # Calculate volatility for company 1
        returns1 = data1['Close'].pct_change().dropna()
        volatility1 = returns1.std() * 100
        
        # Calculate key metrics for company 2
        current_price2 = data2['Close'].iloc[-1]
        start_price2 = data2['Close'].iloc[0]
        change_pct2 = ((current_price2 - start_price2) / start_price2) * 100
        
        # Calculate volatility for company 2
        returns2 = data2['Close'].pct_change().dropna()
        volatility2 = returns2.std() * 100
        
        # Generate plot
        plot_path = Visualizer.plot_stock_comparison(data1, data2, ticker1, ticker2, period)
        
        return {
            "ticker1": ticker1,
            "ticker2": ticker2,
            "period": period,
            "current_price1": current_price1,
            "current_price2": current_price2,
            "change_percent1": change_pct1,
            "change_percent2": change_pct2,
            "volatility1": volatility1,
            "volatility2": volatility2,
            "better_performance": ticker1 if change_pct1 > change_pct2 else ticker2,
            "performance_difference": abs(change_pct1 - change_pct2),
            "lower_volatility": ticker1 if volatility1 < volatility2 else ticker2,
            "volatility_difference": abs(volatility1 - volatility2),
            "plot_path": plot_path
        }
    
    def get_investment_advice(self, ticker):
        """
        Generate investment advice for a stock
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            dict: Investment advice
        """
        # Get technical analysis
        analysis = self.get_technical_analysis(ticker)
        if "error" in analysis:
            return analysis
        
        # Extract key metrics
        current_price = analysis["current_price"]
        ma50 = analysis["ma50"]
        ma200 = analysis["ma200"]
        rsi = analysis["rsi"]
        ma_trend = analysis["ma_trend"]
        rsi_signal = analysis["rsi_signal"]
        
        # Generate short-term advice
        short_term_signals = []
        if current_price > ma50:
            short_term_signals.append(("positive", "Price above 50-day moving average"))
        else:
            short_term_signals.append(("negative", "Price below 50-day moving average"))
            
        if rsi > 70:
            short_term_signals.append(("negative", "RSI indicates overbought conditions"))
        elif rsi < 30:
            short_term_signals.append(("positive", "RSI indicates oversold conditions"))
        
        if analysis["macd"] > analysis["macd_signal"]:
            short_term_signals.append(("positive", "MACD above signal line"))
        else:
            short_term_signals.append(("negative", "MACD below signal line"))
            
        # Count positive and negative signals
        positive_count = sum(1 for signal, _ in short_term_signals if signal == "positive")
        negative_count = sum(1 for signal, _ in short_term_signals if signal == "negative")
        
        # Generate long-term advice
        long_term_signals = []
        if current_price > ma200:
            long_term_signals.append(("positive", "Price above 200-day moving average"))
        else:
            long_term_signals.append(("negative", "Price below 200-day moving average"))
            
        if ma50 > ma200:
            long_term_signals.append(("positive", "Golden cross (50-day MA above 200-day MA)"))
        else:
            long_term_signals.append(("negative", "Death cross (50-day MA below 200-day MA)"))
            
        # Count positive and negative long-term signals
        positive_long = sum(1 for signal, _ in long_term_signals if signal == "positive")
        negative_long = sum(1 for signal, _ in long_term_signals if signal == "negative")
        
        # Determine overall short-term recommendation
        if positive_count > negative_count:
            short_term_recommendation = "Positive - Technical indicators suggest potential short-term upside"
        elif negative_count > positive_count:
            short_term_recommendation = "Negative - Technical indicators suggest potential short-term downside"
        else:
            short_term_recommendation = "Neutral - Mixed technical signals for short-term movement"
            
        # Determine overall long-term recommendation
        if positive_long > negative_long:
            long_term_recommendation = "Positive - Technical indicators suggest potential long-term upside"
        elif negative_long > positive_long:
            long_term_recommendation = "Negative - Technical indicators suggest potential long-term downside"
        else:
            long_term_recommendation = "Neutral - Mixed technical signals for long-term movement"
            
        return {
            "ticker": ticker,
            "current_price": current_price,
            "short_term_signals": short_term_signals,
            "long_term_signals": long_term_signals,
            "short_term_recommendation": short_term_recommendation,
            "long_term_recommendation": long_term_recommendation,
            "disclaimer": "This is algorithmic analysis, not professional financial advice. Always do additional research and consider consulting a financial advisor."
        }