import pandas as pd, numpy as np, pickle, json
from collections import OrderedDict
from copy import copy

MARKET_START = 9 # MUST edit if not int. e.g 8.45 change date string below
MARKET_STARTS = int(MARKET_START * 3600)
MARKET_END = 14.75
MARKET_ENDS = int(MARKET_END *3600 + 2)
MARKET_DURATION = int(MARKET_ENDS - MARKET_STARTS)

######################################## Grab & Parse scraped data ###############################################

def requestPsData():        # Must have server up to run this
    import requests, json
    url = 'http://localhost:5003/api/ps-ohlc-outbound'
    x = requests.post(url, data=None)
    # with open("fake_ps_API_response.pickle", "wb") as file: pickle.dump(x, file)
    data = json.loads(x.text)
    with open("fake_ps_API_response.json", "w") as file: json.dump(data, file)
    return data


def fakeRequestPsData():    # Load a chached response, to test thing without haveing to start server
    with open("fake_ps_API_response.json", "r") as file:
        return  json.load(file)


def parsePsOrder(dataPoints):
    def parseDataPoint(dp):
        a = dp.split("\t")
        hour, minute, second = list(map(int, a[0].split(":")))
        i = hour*3600 + 60*minute + second - MARKET_STARTS
        volume = int(a[1].replace(",", ""))
        price = float(a[2])
        return {'hour': hour,   'minute': minute, 'second': second,
                'price': price, 'volume': volume, 'i': i}
    return [dp for dp in list(map(parseDataPoint, dataPoints)) if dp['i'] <= MARKET_DURATION]

############################################### Raw => OHLC df ###################################################

def createDFfromOrderBook(psOrders):
    prices = [None] * MARKET_DURATION
    volumes = [None] * MARKET_DURATION
    for order in psOrders:
        prices[order['i']] = order['price']
        volumes[order['i']] = order['volume']
    index = pd.date_range(f'29/10/2020 09:00:00',
                          periods=MARKET_DURATION, freq='S')
    return pd.Series(prices, index=index), pd.Series(volumes, index=index)


def ohlcFromPrices(dfPrice, sampleSize='1Min'):
    df = dfPrice.resample(sampleSize).agg(  # series.resample('60s')
        OrderedDict([
            ('open', 'first'),
            ('high', 'max'),
            ('low', 'min'),
            ('close', 'last'),]))
    dic = {}
    for key in ['open', 'high', 'low', 'close']:
        dic[key] = df[key].fillna(method='pad').values
    dic['date'] = list(map(lambda x: x[1], df.index[:len(df['open'])]))
    df = pd.DataFrame.from_dict(dic).set_index('date')
    return df, dic

##################################################################################################################

dfPrice, dfVolume = createDFfromOrderBook(
                        parsePsOrder(fakeRequestPsData()['data']))
df, dic = ohlcFromPrices(dfPrice)

#%%

from math import pi

import pandas as pd

from bokeh.plotting import figure, output_file, show
from bokeh.sampledata.stocks import MSFT

# df = pd.DataFrame(MSFT)[:50]; df["date"] = pd.to_datetime(df["date"])

inc = df.close > df.open
dec = df.open > df.close
w = 12*60*60 # half day in ms

TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
LINE_COLOR = "#111111"
p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1600, title = "MSFT Candlestick")
p.xaxis.major_label_orientation = pi/4
p.grid.grid_line_alpha=0.3
df.date = df.index
p.segment(df.date, df.high, df.date, df.low, color=LINE_COLOR)

p.vbar(df.date[inc], w*1.1, df.open[inc], df.close[inc], fill_color="green", line_color=LINE_COLOR, line_width=0.4)
p.vbar(df.date[dec], w*1.1, df.open[dec], df.close[dec], fill_color="red", line_color=LINE_COLOR, line_width=0.4)

output_file("candlestick.html", title="candlestick.py example")

show(p)  # open a browser

_dic = copy(dic)
#%%
dic = copy(_dic)
KEYS = ['open', 'high', 'low', 'close', 'date']
dd ={}
for key in KEYS: dd[key] = []
for i in range(0, 150):
    for key in KEYS:
        dd[key].append(dic[key][i])
for i in range(240, 330):
    for key in KEYS:
        dd[key].append(dic[key][i])

dic = dd
df = pd.DataFrame.from_dict(dic)
inc = df.close > df.open
dec = df.open > df.close


TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
LINE_COLOR = "#111111"
MID = 150
CANDLE_WIDTH = 0.7

p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1600, title = "MSFT Candlestick")
p.xaxis.major_label_orientation = pi/4
p.grid.grid_line_alpha=0.3

df.date = df.index
p.segment(df.date, df.high, df.date, df.low, color=LINE_COLOR)
p.segment(df.date[150:151], df[150:151], df[150:151]/100, df[150:151]*100, color=LINE_COLOR)

from bokeh.models import Span
vline1 = Span(location=0 - .5, dimension='height', line_color='black', line_width=1)            # Start of day
vline2 = Span(location=MID - .5, dimension='height', line_color='blue', line_width=1)           # Lunch break
vline3 = Span(location=len(df) -1 + .5, dimension='height', line_color='black', line_width=1)   # End of day

p.renderers.extend([vline1, vline2, vline3])
p.vbar(df.date[inc], CANDLE_WIDTH, df.open[inc], df.close[inc], fill_color="green", line_color=LINE_COLOR, line_width=0.4)
p.vbar(df.date[dec], CANDLE_WIDTH, df.open[dec], df.close[dec], fill_color="red", line_color=LINE_COLOR, line_width=0.4)


output_file("candlestick_trimmed.html", title="candlestick.py example")
show(p)
#%%
lst = list(df.index)
lst