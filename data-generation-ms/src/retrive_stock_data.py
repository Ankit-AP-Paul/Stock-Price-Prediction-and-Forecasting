import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def retrive_stock_data(ticker: str):
    load_dotenv()
    
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(DATABASE_URL)
    
    query = f"SELECT * FROM \"{ticker}\""
    data = pd.read_sql_query(text(query), engine)
    
    engine.dispose()
    
    return data
    
