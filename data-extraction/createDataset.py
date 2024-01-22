import yfinance as yf
# import yahoo_fin.stock_info as yf2
import pandas as pd
from rsi.rsi2 import calc_rsi
from MovingAverage.MovingAverage import calculate_sma, calculate_exponential_smoothing, double_EMA
from adx.adx2 import extract_adx
from bbands.bbands import calculate_bbands


def extractData(stock_ticker):
    data = yf.download(tickers=stock_ticker, period='2y', interval='1d')
    data['RSI'] = calc_rsi(data)
    data["SMA"] = calculate_sma(data.Close, window_size=100)
    data["EMA"] = calculate_exponential_smoothing(data.Close, span=10)
    data["DEMA"] = double_EMA(data.Close, span=10)
    data[['DX', 'ADX']] = extract_adx(data)
    calculate_bbands(data)
    pd.DataFrame(data).to_csv(f'backend\data\{stock_ticker}.csv')


def extractInfo(stock_ticker):
    data = yf2.get_quote_table(stock_ticker)
    df = pd.DataFrame(data, index=[0])
    df.insert(0, "Stock Ticker", stock_ticker)
    df.to_csv(f'backend\stock_info\{stock_ticker}.csv', index=False)


file = open('data-extraction\TICKERS.txt', 'r')
for ticker in file:
    extractData(ticker[:-1])
    # extractInfo(ticker[:-1])
