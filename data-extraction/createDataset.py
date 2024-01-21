import yfinance as yf
import pandas as pd


def extractData(stock_ticker):
    data = yf.download(tickers=stock_ticker, period='6mo',
                       prepost=True, actions=True)
    pd.DataFrame(data).to_csv(f'backend\data\{stock_ticker}.csv')


file = open('TICKERS.txt', 'r')
for ticker in file:
    extractData(ticker[:-1])
