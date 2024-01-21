import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
file = open('TICKERS2.txt', 'r')
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")


def extractADX(st):
    url = 'https://www.alphavantage.co/query?function=ADX&symbol=' + \
        st + '&interval=daily&time_period=10&apikey=' + api_key
    r = requests.get(url)
    json_data = r.json()

    data = json_data.get("Technical Analysis: ADX")

    df = pd.DataFrame.from_dict(data).T
    df.to_csv(f'adx\DATA\{st}.csv')
    print(df)


for ticker in file:
    extractADX(ticker[:-1])
