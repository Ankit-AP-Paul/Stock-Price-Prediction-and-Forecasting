import requests
import pandas as pd

url = 'https://www.alphavantage.co/query'
params = {
    'function': 'RSI',
    'symbol': 'TCS.BSE',
    'interval': 'daily',
    'time_period': '5',
    'series_type': 'open',
    'apikey': 'JCH8XM67Y5SA6HMR'
}

r = requests.get(url, params=params)
json_data = r.json()

print(json_data)

data = json_data['Technical Analysis: RSI']

df = pd.DataFrame.from_dict(data).T

print(df)
