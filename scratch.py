from common import *

def appendFile(data, fn=None):
    import json
    from CONSTANT import OUTPUT_TEXT_FILENAME
    if fn is None: fn = OUTPUT_TEXT_FILENAME
    with open(fn,"a+") as file:
        file.write(json.dumps(data) + "\n")
    return

def loadInterval():
    with open("CONSTANT.py", "r") as file:
        lines = file.readlines()
    for line in lines:
        if line.__contains__("SAVE_INTERVAL"):
            return int(line.split("=")[1].strip())


def loadData_2020_10_28():
    import pickle
    fn = "data/data.pickle-14_48_13(150).pickle"
    with open(fn, "rb") as file:
        data = pickle.load(file)
    return data

#%%


import finplot as fplt
import yfinance

df = yfinance.download('AAPL')
fplt.candlestick_ochl(df[['Open', 'Close', 'High', 'Low']])
fplt.show()
#%%
import yfinance as yf
import finplot as fplt

df = yf.download('SPY',start='2018-01-01', end = '2020-04-29')
fplt.candlestick_ochl(df[['Open','Close','High','Low']])
fplt.plot(df.Close.rolling(50).mean())
fplt.plot(df.Close.rolling(200).mean())
fplt.show()
#%%
import plotly.graph_objects as go

import pandas as pd


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

fig = go.Figure(data=go.Ohlc(x=df['Date'],
                open=df['AAPL.Open'],
                high=df['AAPL.High'],
                low=df['AAPL.Low'],
                close=df['AAPL.Close']))
fig.update(layout_xaxis_rangeslider_visible=False)
fig.show()

#%%
import pandas as pd
data = pd.read_csv('/tmp/data/nasdaq100/20160128/AAPL.csv.gz', compression='gzip',
                   error_bad_lines=False)
print(data)

