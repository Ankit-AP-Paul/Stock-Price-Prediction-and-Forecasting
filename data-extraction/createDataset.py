import yfinance as yf
import pandas as pd
from rsi.rsi2 import calc_rsi


def extractData(stock_ticker):
    data = yf.download(tickers=stock_ticker, period='6mo',
                       prepost=True, actions=True)
    calc_rsi(data)
    pd.DataFrame(data).to_csv(f'backend\data\{stock_ticker}.csv')


file = open('data-extraction\TICKERS.txt', 'r')
for ticker in file:
    extractData(ticker[:-1])
