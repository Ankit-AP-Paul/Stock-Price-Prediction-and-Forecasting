import os
from MovingAverage import double_EMA,calculate_exponential_smoothing,calculate_sma
import pandas as pd
import numpy as np

folder_path = 'data1'
file_list = [f for f in os.listdir(folder_path) if f.endswith('.csv')]


def add_features(stock_data):
    stock_data["SMA"]=calculate_sma(stock_data.Close,window_size=100)
    stock_data["EMA"]=calculate_exponential_smoothing(stock_data.Close,span=10)
    stock_data["DEMA"]=double_EMA(stock_data.Close,span=10)


for file_name in file_list:
    stock_data = pd.read_csv(folder_path+'/'+file_name)
    add_features(stock_data=stock_data)
    columns=['Date','Open','High', 'Low', 'Close','SMA','EMA','DEMA']
    df=pd.DataFrame(columns=columns)
    df[columns]=stock_data[columns]
    print(df)
    df.to_csv(f"update_data/{file_name}", index=False)
    print("Done")


    