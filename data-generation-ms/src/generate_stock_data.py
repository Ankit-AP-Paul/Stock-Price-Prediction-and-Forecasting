import yfinance as yf
import pandas as pd
import ta
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


def generate_stock_data(ticker: str):

    load_dotenv()

    data = yf.download(
    tickers=ticker, 
    period="max", 
    interval="1d", 
    auto_adjust=True, 
    prepost=True, 
    threads=True
    )

    data.reset_index(inplace=True)
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    data = ta.add_all_ta_features(
        df=data,
        open="Open", high="High", low="Low", close="Close", volume="Volume",
        fillna=True
    )

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(DATABASE_URL)
    data.to_sql(ticker, engine, if_exists='replace', index=False)

    engine.dispose()

    