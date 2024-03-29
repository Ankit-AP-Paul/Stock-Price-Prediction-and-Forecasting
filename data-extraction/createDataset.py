import yfinance as yf
# import yahoo_fin.stock_info as yf2
import pandas as pd
from rsi.rsi2 import calc_rsi
from MovingAverage.MovingAverage import calculate_sma, calculate_exponential_smoothing, double_EMA
from adx.adx2 import extract_adx
from bbands.bbands import calculate_bbands
from macd.macd import calculate_macd
from stoch.stoch import calculate_stoch
from VWAP.VWAP import calculate_vwap


def extractData(stock_ticker):
    data = yf.download(tickers=stock_ticker, period='5y',
                       interval='1d')
    data['RSI'] = calc_rsi(data)
    data["SMA"] = calculate_sma(data.Close, window_size=100)
    data['13MA'] = calculate_sma(data.Close, window_size=13)
    data['30MA'] = calculate_sma(data.Close, window_size=30)
    data["EMA"] = calculate_exponential_smoothing(data.Close, span=10)
    data["DEMA"] = double_EMA(data.Close, span=10)
    data[['+DI', '-DI', 'DX', 'ADX']] = extract_adx(data)
    data['VWAP'] = calculate_vwap(data)
    calculate_bbands(data)
    calculate_macd(data)
    calculate_stoch(data)

    pd.DataFrame(data).to_csv(f'backend\data\{stock_ticker}.csv')


# def extractInfo(stock_ticker):
#     data = yf2.get_quote_table(stock_ticker)
#     df = pd.DataFrame(data, index=[0])
#     df.insert(0, "Stock Ticker", stock_ticker)
#     df.to_csv(f'backend\stock_info\{stock_ticker}.csv', index=False)


file = open('data-extraction\TICKERS.txt', 'r')
for ticker in file:
    extractData(ticker[:-1])
    # extractInfo(ticker[:-1])
