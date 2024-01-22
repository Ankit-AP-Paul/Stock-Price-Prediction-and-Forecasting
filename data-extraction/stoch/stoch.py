import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_stoch(df, k_period=14, d_period=3):
  Lowest_Low = df['Low'].rolling(window=k_period).min()
  Highest_High = df['High'].rolling(window=k_period).max()
  df['%K'] = ((df['Close'] - Lowest_Low) / (Highest_High - Lowest_Low)) * 100
  df['%D'] = df['%K'].rolling(window=d_period).mean()

