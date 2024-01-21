# fast api tutorial: https://youtu.be/tLKKmouUams?si=0aubactfgcfuCER-

from fastapi import FastAPI
import pandas as pd
import json

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello World"}


@app.get("/get-stock-db")
def get_stock_db(stock_ticker: str):
    try:
        path = f'data/{stock_ticker}.csv'
        df = pd.read_csv(path)
        data = df.to_json(orient='records')
        return json.loads(data)
    except FileNotFoundError:
        return {"message": f"{stock_ticker} not found"}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}
