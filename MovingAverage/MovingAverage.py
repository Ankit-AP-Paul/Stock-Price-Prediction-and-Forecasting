import pandas as pd 
import matplotlib.pyplot as plt 
import yfinance as yf

#stock="AAPL"
# data=yf.download(tickers=stock,period='10y',prepost=True,actions=True)
# print(data.head)


def calculate_sma(data,window_size):
    """
    Calculate Simple Moving Average (SMA) for a given dataset, excluding the specified number of rows.

    Parameters:
    - data: List or numpy array representing the time series data.
    - window_size: Integer representing the window size for the SMA calculation.
    - exclude_rows: Integer representing the number of rows to exclude from the beginning.

    Returns:
    - sma_values: List containing the SMA values with NaN for excluded rows.
    """
    sma_values=[]
    n=len(data)
    for i in range(n-window_size+1):
        window=data[i:i+window_size]
        sma=sum(window)/window_size
        sma_values.append(sma)
    
    #Insert NaN values to the first window_size elements
    sma_values=[None]*(window_size-1)+sma_values
    return sma_values

#data["SMA"]=calculate_sma(data.Close,100)

#print(data)



def calculate_exponential_smoothing(data,span):
    """
    Perform exponential moving average on a given dataset.

    Parameters:
    - data: List or numpy array representing the time series data.
    - span: Smoothing parameter representing the time period.

    Returns:
    - ema_values: List containing the exponential moving average values.

    Formulas:
    - alpha=2/(span+1)

    - EMA(today)=value(today)*alpha + (1-alpha)*EMA(yesterday)


    """
    alpha=2/(span+1)
    n=len(data)
    smoothed_values=[data[0]]

    for i in range(1,n):
        smooth_val=alpha*data[i] +(1-alpha)*smoothed_values[-1]
        smoothed_values.append(smooth_val)
    return smoothed_values
#data["EMA"]=calculate_exponential_smoothing(data.Close,span=10)




def double_EMA(data,span):
    """
    Perform double exponential moving average on a given dataset.

    Parameters:
    - data: List or numpy array representing the time series data.
    - span: Smoothing parameter representing the time period.

    Returns:
    - dema_values: List containing the double exponential moving average values.

    Formulas:
    - DEMA= 2*EMA(N) - EMA(EMA(N))
    """
    dema_values=[]
    EMA1=calculate_exponential_smoothing(data,span)
    EMA2=calculate_exponential_smoothing(EMA1,span)

    dema_values=[2*EMA1[i]-EMA2[i] for i in range(len(data))]

    return dema_values


#data["DEMA"]=double_EMA(data.Close,span=10)

#print(data)





