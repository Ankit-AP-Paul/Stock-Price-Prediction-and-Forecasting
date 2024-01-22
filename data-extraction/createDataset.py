import yfinance as yf
import pandas as pd
from rsi.rsi2 import calc_rsi
from MovingAverage.MovingAverage import calculate_sma, calculate_exponential_smoothing, double_EMA


def extractData(stock_ticker):
    data = yf.download(tickers=stock_ticker, period='2y', interval='1d')
    data['RSI'] = calc_rsi(data)
    data["SMA"] = calculate_sma(data.Close, window_size=100)
    data["EMA"] = calculate_exponential_smoothing(data.Close, span=10)
    data["DEMA"] = double_EMA(data.Close, span=10)
    pd.DataFrame(data).to_csv(f'backend\data\{stock_ticker}.csv')


file = open('data-extraction\TICKERS.txt', 'r')
for ticker in file:
    extractData(ticker[:-1])
