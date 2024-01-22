import numpy as np
import matplotlib.pyplot as plt

def calculate_macd(df):
  ShortEMA = df['Close'].ewm(span=12, adjust=False).mean()
  LongEMA = df['Close'].ewm(span=26, adjust=False).mean()
  df['MACD'] = ShortEMA - LongEMA
  df['Signal_line'] = df['MACD'].ewm(span=9, adjust=False).mean()