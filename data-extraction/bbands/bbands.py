import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt


def calculate_bbands(df):
    MA_30_Close = df['Close'].rolling(window=30).mean()
    STD_20_Close = df['Close'].rolling(window=20).std()

    df['Upper_Band'] = MA_30_Close + 2 * STD_20_Close
    df['Lower_Band'] = MA_30_Close - 2 * STD_20_Close

    print(df)


