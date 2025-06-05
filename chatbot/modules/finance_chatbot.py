import re
import os
import argparse
from modules.config import Config
from modules.stock_data import StockDataService
from modules.company_mapper import CompanyMapper
from modules.stock_analysis import StockAnalyzer
from modules.visualization import Visualizer
from modules.llm_client import LLMClient

class FinanceChatbot:
    """
    Finance chatbot that integrates stock analysis and LLM capabilities
    using a modular architecture for improved maintainability.    """
    
    def __init__(self, api_key=None, model_name=Config.DEFAULT_MODEL, portfolio_file=None):
        """
        Initialize the Finance Chatbot
        
        Args:
            api_key (str): Hugging Face API key. If None, will look for HF_API_KEY environment variable
            model_name (str): Name of the model to use on Hugging Face
            portfolio_file (str): Not used (kept for backward compatibility)
        """
        print("Initializing Finance Chatbot...")
        
        # Initialize components
        self.stock_data_service = StockDataService()
        self.company_mapper = CompanyMapper()
        self.stock_analyzer = StockAnalyzer()
        self.llm_client = LLMClient(api_key, model_name)
        
        print("✓ Modular architecture initialized")
        print("✓ No large models stored locally")
        print("✓ Processing happens on Hugging Face servers")
        print("✓ Minimal storage requirements")
    
    def _get_currency_symbol(self, ticker):
        """
        Get the appropriate currency symbol for a stock ticker
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            str: Currency symbol (₹ for Indian stocks, $ for others)
        """
        return "₹" if self.stock_data_service._is_indian_stock(ticker) else "$"
    
    def get_response(self, user_input):
        """
        Generate a response to the user's input
        
        Args:
            user_input (str): User's input/question
            
        Returns:
            str: Generated response
        """
        print(f"Processing: '{user_input}'")
        user_input_lower = user_input.lower()
        
        # Check if this is a stock buying advice request
        if any(phrase in user_input_lower for phrase in ["should i buy", "worth buying", "good investment", "invest in"]):
            buying_advice = self.handle_stock_buying_advice(user_input)
            if buying_advice:
                return buying_advice
        
        # Check if this is a stock analysis request
        if "analyze" in user_input_lower and any(word in user_input_lower for word in ["stock", "price", "ticker"]):
            analysis_response = self.handle_stock_analysis_request(user_input)
            if analysis_response:
                return analysis_response
        
        # Check for technical analysis pattern (moving averages, RSI, etc.)
        tech_analysis_match = re.search(r'(?:what|how)\s+(?:is|are)\s+(?:the\s+)?(?:moving\s+averages|ma|ma50|ma200|rsi|relative\s+strength|macd|bollinger|fibonacci|technical\s+indicators)(?:\s+for)?(?:\s+([a-z\s]+))?', user_input_lower)
        if tech_analysis_match or "moving average" in user_input_lower:
            technical_analysis = self.handle_technical_analysis_request(user_input)
            if technical_analysis:
                return technical_analysis
        
        # Check for performance analysis
        performance_match = re.search(r'(?:how\s+has|what\s+(?:is|was)\s+(?:the)?\s+performance\s+of)', user_input_lower)
        if performance_match:
            performance_analysis = self.handle_performance_analysis_request(user_input)
            if performance_analysis:
                return performance_analysis
        
        # Check for stock comparison requests
        compare_match = re.search(r'compare\s+([a-z\s]+)\s+(?:and|vs|versus|with|to)\s+([a-z\s]+)', user_input_lower)
        if compare_match:
            comparison = self.handle_stock_comparison_request(user_input)
            if comparison:
                return comparison
        
        # Check for specific price queries
        price_patterns = [
            r'(current )?price of ([a-z\s]+)',
            r'how much (is|does) ([a-z\s]+) (cost|trade for|trading at)',
            r'what\'?s ([a-z\s]+) (trading at|price)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                price_info = self.handle_price_query(user_input)
                if price_info:
                    return price_info
                break        # Before using the LLM, check if we can extract a stock and provide basic info
        # Only do this if the query seems stock-related
        stock_related_keywords = ['stock', 'share', 'price', 'ticker', 'company', 'trading', 'market cap', 'dividend']
        if any(keyword in user_input_lower for keyword in stock_related_keywords):
            company_info = self.company_mapper.extract_company_name(user_input)
            if company_info:
                ticker, full_name, _ = company_info
                try:
                    # Get basic stock info
                    current_price = self.stock_data_service.get_current_price(ticker)
                    if current_price is not None:
                        # Get stock data to calculate change
                        data = self.stock_data_service.get_stock_data(ticker, "5d")
                        if data is not None and not data.empty and len(data) >= 2:
                            change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                            currency_symbol = self._get_currency_symbol(ticker)
                            
                            return f"{full_name} ({ticker}) is currently trading at {currency_symbol}{current_price:.2f}, " + \
                                   f"which is {change:.2f}% {'up' if change >= 0 else 'down'} from the previous close."
                except:
                    pass  # If this fails, continue to LLM        # If not a specific command, use the LLM for general financial advice
        if not self.llm_client.api_key:
            # Use built-in fallback responses instead of just showing error message
            return self.llm_client.get_fallback_response(user_input)
          # Query the LLM
        return self.llm_client.generate_response(user_input)
    
    def handle_stock_buying_advice(self, user_input):
        """Handle stock buying advice request"""
        # Try to extract the company from the user input
        company_info = self.company_mapper.extract_company_name(user_input)
        
        if not company_info:
            return "I couldn't identify a company in your question. Please specify which company you're interested in."
                
        ticker, company_name, _ = company_info
        print(f"Analyzing buying advice for {ticker} ({company_name})")
        
        try:
            # Get stock data and analysis
            analysis = self.stock_analyzer.get_investment_advice(ticker)
            if "error" in analysis:
                return analysis["error"]
            
            currency_symbol = self._get_currency_symbol(ticker)
            response = f"Investment Analysis for {ticker} ({company_name}):\n\n"
            response += f"Current price: {currency_symbol}{analysis['current_price']:.2f}\n\n"
            
            # Add short-term signals
            response += "Short-term indicators:\n"
            for signal_type, description in analysis["short_term_signals"]:
                symbol = "✓" if signal_type == "positive" else "✗"
                response += f"{symbol} {description}\n"
                
            response += f"\nShort-term outlook: {analysis['short_term_recommendation']}\n\n"
            
            # Add long-term signals
            response += "Long-term indicators:\n"
            for signal_type, description in analysis["long_term_signals"]:
                symbol = "✓" if signal_type == "positive" else "✗"
                response += f"{symbol} {description}\n"
                
            response += f"\nLong-term outlook: {analysis['long_term_recommendation']}\n\n"
            
            # Add disclaimer
            response += "Reminder: " + analysis["disclaimer"]
              # Generate and save the plot
            self.stock_analyzer.plot_stock(ticker)
            
            return response
            
        except Exception as e:
            print(f"Error generating buying advice: {e}")
            return f"I encountered an error analyzing {ticker} ({company_name}). Please check if it's a valid ticker symbol."
    
    def handle_stock_analysis_request(self, user_input):
        """Handle stock analysis request"""
        ticker = self.company_mapper.extract_ticker_symbol(user_input)
        if not ticker:
            return None
            
        try:
            analysis = self.stock_analyzer.analyze_stock(ticker)
            if "error" not in analysis:
                currency_symbol = self._get_currency_symbol(ticker)
                response = f"Analysis for {ticker}:\n"
                response += f"Current price: {currency_symbol}{analysis['current_price']}\n"
                response += f"Change: {analysis['change_percent']}%\n"
                response += f"Average volume: {analysis['volume']}\n"
                response += f"RSI (14-day): {analysis['rsi']}\n"
                response += f"Trend: {analysis['trend']}\n"
                response += f"I've also generated a plot for {ticker} that you can view."
                self.stock_analyzer.plot_stock(ticker)
                return response
            else:
                return analysis["error"]
        except Exception as e:
            print(f"Error in stock analysis: {e}")
            return None
    
    def handle_technical_analysis_request(self, user_input):
        """Handle technical analysis request"""
        # Extract company name
        company_info = self.company_mapper.extract_company_name(user_input)
        if not company_info:
            return None
        
        ticker, full_name, _ = company_info
        try:
            # Get technical analysis
            analysis = self.stock_analyzer.get_technical_analysis(ticker)
            if "error" in analysis:
                return analysis["error"]
            
            # Format the response
            currency_symbol = self._get_currency_symbol(ticker)
            response = f"Technical Analysis for {full_name} ({ticker}):\n\n"
            response += f"Current Price: {currency_symbol}{analysis['current_price']:.2f}\n"
            response += f"50-day Moving Average: {currency_symbol}{analysis['ma50']:.2f}\n"
            response += f"200-day Moving Average: {currency_symbol}{analysis['ma200']:.2f}\n"
            response += f"RSI (14-day): {analysis['rsi']:.2f}\n\n"
            
            response += f"Current Trend: {analysis['ma_trend']} (50-day MA is {'above' if analysis['ma50'] > analysis['ma200'] else 'below'} 200-day MA)\n"
            
            # Add interpretation
            response += f"{analysis['price_vs_ma50']}\n"
            response += f"{analysis['price_vs_ma200']}\n"
            
            if analysis['rsi_signal'] == "Overbought":
                response += "RSI indicates the stock may be overbought at current levels.\n"
            elif analysis['rsi_signal'] == "Oversold":
                response += "RSI indicates the stock may be oversold at current levels.\n"
            else:
                response += "RSI is in neutral territory, neither overbought nor oversold.\n"
            
            # Generate and save plot
            self.stock_analyzer.plot_stock(ticker)
            
            return response
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return None
    
    def handle_performance_analysis_request(self, user_input):
        """Handle performance analysis request"""
        # Extract company name
        company_info = self.company_mapper.extract_company_name(user_input)
        if not company_info:
            return None
            
        ticker, full_name, _ = company_info
        
        # Determine time period
        yfinance_period = "1y"  # Default technical period for yfinance
        display_period = "1 year"  # Human-readable period for display
        user_input_lower = user_input.lower()        # Extract numeric duration and unit from user input
        duration_match = re.search(r'(\d+)\s*(day|days|week|weeks|month|months|year|years)', user_input_lower)
        if duration_match:
            duration = int(duration_match.group(1))
            unit = duration_match.group(2)
            
            # Store the requested duration for display
            if unit in ['day', 'days']:
                display_period = f"{duration} {'day' if duration == 1 else 'days'}"
                if duration <= 60:
                    yfinance_period = f"{duration}d"
                else:
                    # For longer periods, convert to appropriate format for yfinance
                    yfinance_period = f"{duration}d"  # Now using start/end dates, can keep this format            elif unit in ['week', 'weeks']:
                display_period = f"{duration} {'week' if duration == 1 else 'weeks'}"
                yfinance_period = f"{duration * 7}d"  # Convert to days
            elif unit in ['month', 'months']:
                display_period = f"{duration} {'month' if duration == 1 else 'months'}"
                yfinance_period = f"{duration}mo"  # Now using start/end dates, can keep this format
            elif unit in ['year', 'years']:
                display_period = f"{duration} {'year' if duration == 1 else 'years'}"
                yfinance_period = f"{duration}y"
        else:
            # Handle specific period phrases
            if "1 month" in user_input_lower or "1m" in user_input_lower or "one month" in user_input_lower:
                display_period = "1 month"
                yfinance_period = "1mo"
            elif "3 months" in user_input_lower or "3m" in user_input_lower or "three months" in user_input_lower:
                display_period = "3 months"
                yfinance_period = "3mo"
            elif "6 months" in user_input_lower or "6m" in user_input_lower or "six months" in user_input_lower:
                display_period = "6 months"
                yfinance_period = "6mo"
            elif "5 years" in user_input_lower or "5y" in user_input_lower or "five years" in user_input_lower:
                display_period = "5 years"
                yfinance_period = "5y"
            elif "last year" in user_input_lower or "past year" in user_input_lower:
                display_period = "1 year"
                yfinance_period = "1y"
            elif "2 years" in user_input_lower or "two years" in user_input_lower:
                display_period = "2 years"
                yfinance_period = "2y"
            
        print(f"Using period: {yfinance_period} for performance analysis")
        
        try:
            # Get stock data
            data = self.stock_data_service.get_stock_data(ticker, period=yfinance_period)
            
            if data is None or data.empty:
                return f"I couldn't retrieve performance data for {full_name} ({ticker})."
                
            # Calculate performance metrics
            start_price = data['Close'].iloc[0]
            current_price = data['Close'].iloc[-1]
            absolute_change = current_price - start_price
            percentage_change = (absolute_change / start_price) * 100
            
            # Calculate high and low
            high_price = data['Close'].max()
            low_price = data['Close'].min()
            high_date = data['Close'].idxmax().strftime('%Y-%m-%d')
            low_date = data['Close'].idxmin().strftime('%Y-%m-%d')
              # Calculate volatility
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std() * 100
            
            # Format the response
            currency_symbol = self._get_currency_symbol(ticker)
            response = f"Performance Analysis for {full_name} ({ticker}) over the past {display_period}:\n\n"
            response += f"Starting Price: {currency_symbol}{start_price:.2f} (on {data.index[0].strftime('%Y-%m-%d')})\n"
            response += f"Current Price: {currency_symbol}{current_price:.2f} (on {data.index[-1].strftime('%Y-%m-%d')})\n"
            response += f"Absolute Change: {currency_symbol}{absolute_change:.2f}\n"
            response += f"Percentage Change: {percentage_change:.2f}%\n\n"
            
            response += f"Highest Price: {currency_symbol}{high_price:.2f} (on {high_date})\n"
            response += f"Lowest Price: {currency_symbol}{low_price:.2f} (on {low_date})\n"
            response += f"Volatility: {volatility:.2f}%\n\n"
            
            # Add interpretation
            if percentage_change > 0:
                response += f"{ticker} has performed positively over this period, gaining {percentage_change:.2f}%.\n"
            else:
                response += f"{ticker} has performed negatively over this period, losing {abs(percentage_change):.2f}%.\n"
            
            if volatility > 30:
                response += "The stock has shown high volatility during this period.\n"
            elif volatility > 15:
                response += "The stock has shown moderate volatility during this period.\n"
            else:
                response += "The stock has shown relatively low volatility during this period.\n"
            
            # Generate and save the plot
            plot_path = self.stock_analyzer.plot_stock(ticker, period=yfinance_period)
            if plot_path:
                response += f"\nA chart has been saved to {plot_path}."
                
            return response
            
        except Exception as e:
            print(f"Error in performance analysis: {e}")
            return None
    
    def handle_stock_comparison_request(self, user_input):
        """Handle stock comparison request"""
        compare_match = re.search(r'compare\s+([a-z\s]+)\s+(?:and|vs|versus|with|to)\s+([a-z\s]+)', user_input.lower())
        if not compare_match:
            return None
            
        company1 = compare_match.group(1).strip()
        company2 = compare_match.group(2).strip()
        
        company_info1 = self.company_mapper.extract_company_name(company1)
        company_info2 = self.company_mapper.extract_company_name(company2)
        
        if not company_info1 or not company_info2:
            if not company_info1 and not company_info2:
                return "I couldn't identify either company. Please use more specific company names."
            elif not company_info1:
                return f"I couldn't identify the first company '{company1}'. Please use a more specific name."
            else:
                return f"I couldn't identify the second company '{company2}'. Please use a more specific name."
        
        ticker1, full_name1, _ = company_info1
        ticker2, full_name2, _ = company_info2
        
        try:
            # Get comparison data
            comparison = self.stock_analyzer.get_stock_comparison(ticker1, ticker2)
            
            if "error" in comparison:
                return comparison["error"]
            
            # Format response
            response = f"Comparison of {full_name1} ({ticker1}) vs {full_name2} ({ticker2}):\n\n"
            
            # Current price information
            currency_symbol1 = self._get_currency_symbol(ticker1)
            currency_symbol2 = self._get_currency_symbol(ticker2)
            response += f"{ticker1} Current Price: {currency_symbol1}{comparison['current_price1']:.2f}\n"
            response += f"{ticker2} Current Price: {currency_symbol2}{comparison['current_price2']:.2f}\n\n"
            
            # Performance comparison
            response += f"Performance (1 year):\n"
            response += f"{ticker1}: {comparison['change_percent1']:+.2f}%\n"
            response += f"{ticker2}: {comparison['change_percent2']:+.2f}%\n"
            response += f"Difference: {comparison['performance_difference']:.2f}% in favor of {comparison['better_performance']}\n\n"
            
            # Volatility comparison
            response += f"Volatility (Risk):\n"
            response += f"{ticker1}: {comparison['volatility1']:.2f}%\n"
            response += f"{ticker2}: {comparison['volatility2']:.2f}%\n"
            response += f"{comparison['lower_volatility']} has shown lower volatility, indicating potentially lower risk.\n\n"
            
            # Add overall assessment
            better_performer = comparison['better_performance']
            lower_risk = comparison['lower_volatility']
            
            if better_performer == lower_risk:
                response += f"Overall, {better_performer} has demonstrated both better performance and lower risk over the past year.\n"
            else:
                response += f"This presents a classic risk-return tradeoff: {better_performer} has shown better returns while {lower_risk} has demonstrated lower risk.\n"
                
            # Mention plot
            if comparison['plot_path']:
                response += f"A comparative chart has been saved to {comparison['plot_path']}."
                
            return response
            
        except Exception as e:
            print(f"Error in stock comparison: {e}")
            return None
    
    def handle_price_query(self, user_input):
        """Handle stock price query"""
        # Get the company name from the query
        company_info = self.company_mapper.extract_company_name(user_input)
        
        if not company_info:
            return None
            
        ticker, full_name, _ = company_info
        
        # Get the current price directly
        try:
            current_price = self.stock_data_service.get_current_price(ticker)
            if current_price is not None:
                currency_symbol = self._get_currency_symbol(ticker)
                return f"The current price of {full_name} ({ticker}) is {currency_symbol}{current_price:.2f}."
            else:
                return f"I couldn't retrieve the current price data for {full_name} ({ticker})."
        except Exception as e:
            print(f"Error getting price: {e}")
            return f"I encountered an error retrieving price information for {full_name} ({ticker})."