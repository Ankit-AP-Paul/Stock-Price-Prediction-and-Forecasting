# fast api tutorial: https://youtu.be/tLKKmouUams?si=0aubactfgcfuCER-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5000",
    "https://stock-prediction-website.vercel.app",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/get-stock-info")
def get_stock_info(stock_ticker: str):
    try:
        path = f'stock_info/{stock_ticker}.csv'
        df = pd.read_csv(path)
        data = df.to_json(orient='records')
        return json.loads(data)
    except FileNotFoundError:
        return {"message": f"{stock_ticker} not found"}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}


@app.get("/get-companies")
def get_companies():
    try:
        path = 'companies.csv'
        df = pd.read_csv(path)
        data = df.to_json(orient='records')
        return json.loads(data)
    except FileNotFoundError:
        return {"message": f"companies.csv not found"}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}
