from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.generate_stock_data import generate_stock_data
from src.retrive_stock_data import retrive_stock_data
from src.generate_stock_info import generate_stock_info
import pandas as pd

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "Data Generation microservice is running!", "status": 200}


@app.get("/generate-data", tags=["Data Generation"])
def generate_data():
    try:
        file = open('src/tickers.txt', 'r')
        for ticker in file:
            ticker = ticker.strip()
            if ticker:
                generate_stock_data(ticker)
        return {"message": "Data generation completed successfully", "status": 200}
    except Exception as e:
        return {"message": f"Error generating stock data: {str(e)}", "status": 500}
    finally:
        file.close()

@app.get("/generate-stock-info", tags=["Data Generation"])
def generate_info():
    generate_stock_info()

@app.get("/retrive-data", tags=["Data Retrieval"])
def retrive_data(ticker: str):
    try:
        data = retrive_stock_data(ticker)
        for col in data.select_dtypes(include=['datetime64']).columns:
            data[col] = data[col].dt.strftime('%Y-%m-%d')
        data_dict = data.to_dict(orient="records")
        return {"data": data_dict, "message": "Stock data retrieved successfully", "status": 200}
    except Exception as e:
        return {"message": f"Error retrieving stock data: {str(e)}", "status": 500}
