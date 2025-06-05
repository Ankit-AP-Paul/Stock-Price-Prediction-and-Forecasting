import os

class Config:
    """Configuration settings for the Finance Chatbot application"""    # API settings
    API_KEY = os.environ.get("HF_API_KEY")
    DEFAULT_MODEL = "microsoft/DialoGPT-medium"  # Better model for conversation
    
    # Stock data settings
    DEFAULT_PERIOD = "1y"
    
    # Indian stocks that require special handling
    INDIAN_STOCKS = [
        "TCS", "INFY", "WIPRO", "RELIANCE", "TATAMOTORS", "ICICIBANK",
        "HDFCBANK", "HDFC", "SBIN", "AXISBANK", "SUNPHARMA", "MARUTI", 
        "ITC", "CIPLA", "BRITANNIA", "KOTAKBANK", "HEROMOTOCO", "BAJAJ-AUTO"
    ]