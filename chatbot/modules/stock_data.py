import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import time
import random
from modules.config import Config

class StockDataService:
    """Service for retrieving and managing stock data"""
    
    def __init__(self):
        """Initialize the stock data service"""
        self.stock_data_cache = {}
        
    def get_stock_data(self, ticker, period=Config.DEFAULT_PERIOD):
        """
        Get historical stock data for a given ticker
        Supports both international markets and Indian markets
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period for historical data
            
        Returns:
            pandas.DataFrame: Historical stock data
        """
        # Check cache first
        cache_key = f"{ticker}_{period}"
        if cache_key in self.stock_data_cache:
            return self.stock_data_cache[cache_key]
            
        try:
            # Convert period to start and end dates for more precise control
            end_date = datetime.now()
            
            # Parse the period string to determine the start date
            if period.endswith('d'):
                days = int(period[:-1])
                start_date = end_date - pd.DateOffset(days=days)
            elif period.endswith('mo'):
                months = int(period[:-2])
                start_date = end_date - pd.DateOffset(months=months)
            elif period.endswith('y'):
                years = int(period[:-1])
                start_date = end_date - pd.DateOffset(years=years)
            else:
                # Default to 1 year if format not recognized
                start_date = end_date - pd.DateOffset(years=1)
                
            print(f"Fetching data for {ticker} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Check if it's an Indian stock (NSE or BSE)
            is_indian_stock = self._is_indian_stock(ticker)
            
            if is_indian_stock:
                data = self._get_indian_stock_data(ticker, period, start_date, end_date)
            else:
                # Use yfinance for non-Indian stocks
                stock = yf.Ticker(ticker)
                # Use start and end instead of period for more precise control
                data = stock.history(start=start_date, end=end_date)
                
                if data.empty:
                    print(f"No data found for {ticker} using yfinance")
                    return None
                    
                # Calculate moving averages
                data['MA50'] = data['Close'].rolling(window=50).mean()
                data['MA200'] = data['Close'].rolling(window=200).mean()
            
            # Cache the data if not empty
            if data is not None and not data.empty:
                self.stock_data_cache[cache_key] = data
                
            return data
            
        except Exception as e:
            print(f"Error retrieving stock data for {ticker}: {e}")
            return None
            
    def _is_indian_stock(self, ticker):
        """
        Check if a ticker is from Indian markets
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            bool: True if it's an Indian stock, False otherwise
        """
        # Indian tickers usually end with .NS (NSE) or .BO (BSE)
        if ticker.endswith(('.NS', '.BO')):
            return True
              # Check if it's in our list of known Indian stocks
        base_ticker = ticker.split('.')[0]
        if base_ticker in Config.INDIAN_STOCKS:
            return True
                
        return False
        
    def _get_indian_stock_data(self, ticker, period="1y", start_date=None, end_date=None):
        """
        Get data for Indian stocks using multiple sources with retry logic
        """
        print(f"Getting Indian stock data for {ticker} with period {period}")
        if start_date and end_date:
            print(f"Using date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Start with Yahoo Finance direct API since it's consistently working
        print(f"Trying Yahoo Finance direct API first for {ticker}...")
        real_data = self._try_yahoo_finance_direct(ticker, start_date, end_date, period)
        if real_data is not None:
            return real_data
        
        # Fallback to yfinance if direct API fails
        if not ticker.endswith(('.NS', '.BO')):
            print(f"Yahoo Finance direct API failed for {ticker}, trying yfinance as fallback...")
            # Try NSE first, then BSE with retry logic
            for suffix in ['.NS', '.BO']:
                for attempt in range(2):  # Reduced attempts since direct API is primary
                    try:
                        # Add random delay to avoid rate limiting
                        if attempt > 0:
                            delay = random.uniform(1, 3) * (attempt + 1)
                            print(f"Retrying {ticker}{suffix} after {delay:.1f}s delay (attempt {attempt + 1})")
                            time.sleep(delay)
                        
                        stock = yf.Ticker(ticker + suffix)
                        
                        # If we have start_date and end_date, use them instead of period
                        if start_date and end_date:
                            data = stock.history(start=start_date, end=end_date)
                        else:
                            data = stock.history(period=period)
                            
                        if not data.empty:
                            print(f"Retrieved data for {ticker}{suffix} via yfinance (attempt {attempt + 1})")
                            # Calculate moving averages
                            data['MA50'] = data['Close'].rolling(window=50).mean()
                            data['MA200'] = data['Close'].rolling(window=200).mean()
                            return data
                    except Exception as e:
                        print(f"Error with {ticker}{suffix} (attempt {attempt + 1}): {e}")
                        if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                            continue  # Try next attempt
                        if attempt == 1:  # Last attempt (reduced from 2)
                            break
        
        # Try NSE India API as additional fallback
        real_data = self._try_nse_api(ticker, start_date, end_date, period)
        if real_data is not None:
            return real_data
          # Try other free APIs
        real_data = self._try_alternative_apis(ticker, start_date, end_date, period)
        if real_data is not None:
            return real_data
        
        print(f"All real data sources failed for {ticker}. This might be due to:")
        print("1. Rate limiting - try again in a few minutes")
        print("2. Network issues or API changes")
        print("3. Invalid ticker symbol")
        print("Suggestion: Try US stocks (AAPL, MSFT, GOOGL) which have better API support")
        
        return None  # Return None instead of mock data
    
    def _try_yahoo_finance_direct(self, ticker, start_date, end_date, period):
        """Try Yahoo Finance direct API"""
        try:
            base_ticker = ticker.split('.')[0]
            
            # Use range parameter for better results, similar to the working example
            # Convert period to Yahoo Finance range format
            if period.endswith('d'):
                range_param = period
            elif period.endswith('mo'):
                range_param = period
            elif period.endswith('y'):
                range_param = period
            else:
                range_param = "1y"  # Default to 1 year
            
            # Different URL patterns to try with range and interval parameters
            url_patterns = [
                f"https://query1.finance.yahoo.com/v8/finance/chart/{base_ticker}.NS?range={range_param}&interval=1d",
                f"https://query1.finance.yahoo.com/v8/finance/chart/{base_ticker}.BO?range={range_param}&interval=1d",
                f"https://query2.finance.yahoo.com/v8/finance/chart/{base_ticker}.NS?range={range_param}&interval=1d"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            for url in url_patterns:
                try:
                    print(f"Trying Yahoo Finance direct API: {url}")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                            result = data['chart']['result'][0]
                            if 'timestamp' in result and 'indicators' in result:
                                timestamps = result['timestamp']
                                quotes = result['indicators']['quote'][0]
                                
                                # Convert to DataFrame
                                df = pd.DataFrame({
                                    'Open': quotes.get('open', []),
                                    'High': quotes.get('high', []),
                                    'Low': quotes.get('low', []),
                                    'Close': quotes.get('close', []),
                                    'Volume': quotes.get('volume', [])
                                })
                                  # Convert timestamps to dates
                                df.index = pd.to_datetime([datetime.fromtimestamp(ts) for ts in timestamps])
                                
                                if not df.empty:
                                    # Remove rows with NaN values
                                    df = df.dropna()
                                    
                                    # Calculate moving averages
                                    df['MA50'] = df['Close'].rolling(window=50).mean()
                                    df['MA200'] = df['Close'].rolling(window=200).mean()
                                    print(f"Retrieved data via Yahoo Finance direct API")
                                    return df
                except Exception as e:
                    print(f"Error with {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Yahoo Finance direct API error: {e}")
        
        return None
    
    def _try_nse_api(self, ticker, start_date, end_date, period):
        """Try NSE India API with better implementation"""
        try:
            base_ticker = ticker.split('.')[0]
            
            # Better headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.nseindia.com/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # First get the main page to establish session
            session = requests.Session()
            try:
                session.get('https://www.nseindia.com', headers=headers, timeout=10)
                time.sleep(1)  # Small delay
            except:
                pass
            
            # Calculate date range
            if start_date and end_date:
                api_start_date = start_date.strftime("%d-%m-%Y")
                api_end_date = end_date.strftime("%d-%m-%Y")
            else:
                api_end_date = datetime.now().strftime("%d-%m-%Y")
                if period.endswith('d'):
                    days = int(period[:-1])
                    api_start_date = (datetime.now() - pd.DateOffset(days=days)).strftime("%d-%m-%Y")
                elif period.endswith('mo'):
                    months = int(period[:-2])
                    api_start_date = (datetime.now() - pd.DateOffset(months=months)).strftime("%d-%m-%Y")
                elif period.endswith('y'):
                    years = int(period[:-1])
                    api_start_date = (datetime.now() - pd.DateOffset(years=years)).strftime("%d-%m-%Y")
                else:
                    api_start_date = (datetime.now() - pd.DateOffset(years=1)).strftime("%d-%m-%Y")
            
            print(f"Requesting NSE data from {api_start_date} to {api_end_date}")
            
            # Try NSE historical data API
            url = f"https://www.nseindia.com/api/historical/cm/equity?symbol={base_ticker}&series=[%22EQ%22]&from={api_start_date}&to={api_end_date}"
            
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data_json = response.json()
                if 'data' in data_json and data_json['data']:
                    # Convert to DataFrame
                    df = pd.DataFrame(data_json['data'])
                    
                    # Rename columns to match yfinance format
                    df['Date'] = pd.to_datetime(df['CH_TIMESTAMP'])
                    df['Open'] = pd.to_numeric(df['CH_OPENING_PRICE'], errors='coerce')
                    df['High'] = pd.to_numeric(df['CH_TRADE_HIGH_PRICE'], errors='coerce')
                    df['Low'] = pd.to_numeric(df['CH_TRADE_LOW_PRICE'], errors='coerce')
                    df['Close'] = pd.to_numeric(df['CH_CLOSING_PRICE'], errors='coerce')
                    df['Volume'] = pd.to_numeric(df['CH_TOT_TRADED_QTY'], errors='coerce')
                    
                    # Set index and calculate moving averages
                    df.set_index('Date', inplace=True)
                    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                    
                    if not df.empty:
                        df['MA50'] = df['Close'].rolling(window=50).mean()
                        df['MA200'] = df['Close'].rolling(window=200).mean()
                        print(f"Retrieved data for {ticker} via NSE India API")
                        return df
                        
        except Exception as e:
            print(f"NSE API error: {e}")
        
        return None
    
    def _try_alternative_apis(self, ticker, start_date, end_date, period):
        """Try other free financial APIs"""        # This is where you could add other free APIs like:
        # - Alpha Vantage (free tier)
        # - Financial Modeling Prep (free tier)
        # - IEX Cloud (free tier)
        # For now, return None
        return None

    def get_current_price(self, ticker):
        """
        Get the current price for a stock ticker
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            float: Current price or None if not available
        """
        data = self.get_stock_data(ticker, period="5d")
        if data is not None and not data.empty:
            # Get the last valid (non-NaN) close price
            valid_close_prices = data['Close'].dropna()
            if not valid_close_prices.empty:
                return valid_close_prices.iloc[-1]
        return None
        
    def clear_cache(self):
        """Clear the stock data cache"""
        self.stock_data_cache = {}
