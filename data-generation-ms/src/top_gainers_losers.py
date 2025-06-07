import pandas as pd
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def get_stock_data(ticker):
    load_dotenv()
    
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(DATABASE_URL)
    
    query = f"SELECT * FROM \"{ticker}\""
    data = pd.read_sql_query(text(query), engine)
    
    engine.dispose()
    
    return data

def calculate_monthly_performance(ticker):
    try:
        data = get_stock_data(ticker)

        data['Date'] = pd.to_datetime(data['Date'])
        
        data = data.sort_values('Date')

        latest_date = data['Date'].max()
        prev_date = latest_date - timedelta(days=30)
        
        latest_price = data.loc[data['Date'] == latest_date, 'Close'].iloc[0]

        month_ago_data = data[data['Date'] >= prev_date]
        if len(month_ago_data) == 0:
            print(f"Warning: No data found for {ticker} from 1 month ago")
            return None
        
        month_ago_price = month_ago_data['Close'].iloc[0]

        pct_change = ((latest_price - month_ago_price) / month_ago_price) * 100
        
        return {
            'ticker': ticker,
            'current_price': latest_price,
            'month_ago_price': month_ago_price,
            'percentage_change': pct_change,
        }
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return None

def find_top_gainers_losers():

    try:
        with open('src/tickers.txt', 'r') as f:
            tickers = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("Error: tickers.txt file not found")
        return {"message": f"Error generating top gainers and losers: {str(e)}", "status": 500}
    
    print(f"Processing {len(tickers)} tickers...")
    
    results = []
    for i, ticker in enumerate(tickers, 1):
        print(f"Processing {ticker} ({i}/{len(tickers)})")
        result = calculate_monthly_performance(ticker)
        if result:
            results.append(result)
    
    if not results:
        print("No valid results found")
        return

    df = pd.DataFrame(results)
    
    df_sorted = df.sort_values('percentage_change', ascending=False)

    try:
        load_dotenv()

        DATABASE_URL = os.environ.get("DATABASE_URL")

        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")

        engine = create_engine(DATABASE_URL)
        df_sorted.to_sql("percentage_change", engine, if_exists='replace', index=False)

        engine.dispose()


        return {"message": f"Top gainers and losers generated successfully", "status": 200}
    except Exception as e:
        return {"message": f"Error generating top gainers and losers: {str(e)}", "status": 500}
