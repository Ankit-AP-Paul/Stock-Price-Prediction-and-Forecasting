
import yfinance as yf
import pandas as pd
from rsi.rsi2 import calc_rsi
from MovingAverage.MovingAverage import calculate_sma, calculate_exponential_smoothing, double_EMA
from adx.adx2 import extract_adx
from bbands.bbands import calculate_bbands
from macd.macd import calculate_macd
from stoch.stoch import calculate_stoch
from VWAP.VWAP import calculate_vwap


def calculate_output(profit):
    if 0 <= profit <= 0.5:
        return 3
    elif 0.5 < profit < 2:
        return 4
    elif profit > 2:
        return 5
    elif -2 < profit < 0:
        return 2
    elif profit < -2:
        return 1


def createDataset(stock_ticker):
    data = yf.download(tickers=stock_ticker, period='1y',
                       prepost=True, actions=True)
    # data.insert(4, 'Prev Adj Close', data['Adj Close'].shift(1))
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
    data['Profit'] = ((data['Adj Close'] -
                      data['Adj Close'].shift(1)) / data['Adj Close'].shift(1)) * 100
    data['Output'] = data['Profit'].apply(calculate_output)

    df1 = data.tail(1)
    df1 = df1.reset_index()
    df1 = df1.drop('Date', axis=1)
    df1.insert(0, 'Stock', stock_ticker)

    # print(df1)
    return df1


file = open('data-extraction\TICKERS.txt', 'r')
df = pd.DataFrame()
for ticker in file:
    df1 = createDataset(ticker[:-1])
    df = pd.concat([df, df1], axis=0, ignore_index=True)
# print(df)
pd.DataFrame(df).to_csv('models\dataset.csv', index=False)
