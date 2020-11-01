import pandas as pd, numpy as np, pickle, json
from collections import OrderedDict
from copy import copy
from math import pi
from bokeh.plotting import figure, output_file, show
from bokeh.models import Span, CrosshairTool, HoverTool, ResetTool, PanTool, WheelZoomTool, ColumnDataSource
from bokeh.layouts import layout, column, row
from bokeh.models import Span
from bokeh import events
from bokeh.io import output_file, show
from bokeh.layouts import column, row
from bokeh.models import Button, CustomJS, Div
from bokeh.plotting import figure
from  pandas._libs.tslibs.timestamps import Timestamp
from pandas import Timedelta
from CONSTANT import *

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
        i = compute_i(hour, minute, second)
        volume = int(a[1].replace(",", ""))
        price = float(a[2])
        return {'hour': hour,   'minute': minute, 'second': second,
                'price': price, 'volume': volume, 'i': i}
    lst = list(map(parseDataPoint, dataPoints))
    return [dp for dp in lst if dp['i'] <= MARKET_DURATION], lst[-1]


############################################### Raw => OHLC df ###################################################

def createDFfromOrderBook(psOrders, DATE):
    prices = [None] * MARKET_DURATION
    volumes = [None] * MARKET_DURATION
    for order in psOrders:
        prices[order['i']] = order['price']
        volumes[order['i']] = order['volume']
    index = pd.date_range(f'{DATE} 09:00:00',
                          periods=MARKET_DURATION, freq='S')
    return pd.Series(prices, index=index), pd.Series(volumes, index=index)


def ohlcFromPrices(priceSeries, volumeSeries, sampleSize='1Min'):
    resampled = priceSeries.resample(sampleSize).agg(  # series.resample('60s')
        OrderedDict([
            ('open', 'first'),
            ('high', 'max'),
            ('low', 'min'),
            ('close', 'last'),]))
    dic = {}
    for key in ['open', 'high', 'low', 'close']:
        dic[key] = resampled[key].fillna(method='pad').values
    dic['date'] = list(map(lambda x: x[1], resampled.index[:len(resampled['open'])]))
    dic['vol'] = volumeSeries.resample('1Min').agg(sum).values
    df = pd.DataFrame.from_dict(dic).set_index('date')
    return df, dic, resampled

##################################################################################################################

OHLC_TOOLS = "pan,box_zoom,reset,save"
OHLC_LINE_COLOR = "#111111"
OHLC_TITLE = "VN30F1M Candlestick"
OHLC_PLOT_WIDTH = 1500
OHLC_PLOT_HEIGHT = 400
OHLC_CANDLE_WIDTH = 0.45 * 100000                # HARDCODED
OHLC_TRIMMED_CANDLE_WIDTH = 0.7                  # HARDCODED
OHLC_KEYS = ['open', 'high', 'low', 'close', 'date', 'vol']

def plotPsUntrimmed(df):        # Index is time
    inc = df.close > df.open
    dec = df.open >= df.close
    p = figure(x_axis_type="datetime", tools=OHLC_TOOLS, plot_width=1600, title = OHLC_TITLE)
    p.xaxis.major_label_orientation = pi/3
    p.grid.grid_line_alpha=0.3
    p.segment(df.index, df.high, df.index, df.low, color=OHLC_LINE_COLOR)
    p.vbar(df.index[inc], OHLC_CANDLE_WIDTH, df.open[inc], df.close[inc], fill_color="green", line_color=OHLC_LINE_COLOR, line_width=0.4)
    p.vbar(df.index[dec], OHLC_CANDLE_WIDTH, df.open[dec], df.close[dec], fill_color="red", line_color=OHLC_LINE_COLOR, line_width=0.4)
    wheel_zoom = WheelZoomTool()
    p.add_tools(wheel_zoom)
    p.toolbar.active_scroll = wheel_zoom
    return p


def plotPsTrimmed(df):          # Index is rather meaningless 'i'
    redCandleAlpha = [0] * len(df)
    for i in range(len(df)):
        if df.open.values[i] > df.close.values[i]: redCandleAlpha[i] = 1
    p = figure(x_axis_type="datetime", tools=OHLC_TOOLS,
               plot_width=OHLC_PLOT_WIDTH,
               plot_height=OHLC_PLOT_HEIGHT,
               title ="VN301M Candlestick")
    p.xaxis.major_label_orientation = pi/2
    p.grid.grid_line_alpha=0.3

    source = ColumnDataSource(dict(
        x = df.index,
        open = df.open,
        high = df.high,
        low = df.low,
        close = df.close,
        vol = df.vol,
        redCandleAlpha = redCandleAlpha,
    ))

    p.segment('x', "high", 'x', 'low', source=source, color=OHLC_LINE_COLOR)
    p.vbar(x='x', width=OHLC_TRIMMED_CANDLE_WIDTH, top='open', bottom='close', source=source,
           fill_color="green", line_color=OHLC_LINE_COLOR, line_width=0.4)
    p.vbar('x', OHLC_TRIMMED_CANDLE_WIDTH, 'open', 'close', source=source, line_width=0.4,
           fill_color="red", line_color=OHLC_LINE_COLOR, alpha='redCandleAlpha')

    vline1 = Span(location=0 - .5, dimension='height', line_color='black', line_width=1)            # Start of day
    vline2 = Span(location=MID - .5, dimension='height', line_color='blue', line_width=1)           # Lunch break
    vline3 = Span(location=len(df) -1 + .5, dimension='height', line_color='black', line_width=1)   # End of day
    p.renderers.extend([vline1, vline2, vline3])

    p.add_tools(CrosshairTool(dimensions="both"))
    wheel_zoom = WheelZoomTool()
    p.add_tools(wheel_zoom)
    p.toolbar.active_scroll = wheel_zoom
    return p

def display_event(div, attributes=[], style = 'float:left;clear:left;font_size=13px'):
    "Build a suitable CustomJS to display the current event in the div model."
    return CustomJS(args=dict(div=div), code="""
        var attrs = %s; 
        var args = [];
        const foo = x => {
            x = parseFloat(x) + 0.5
            if (x > 150) x += 90
            x += 9 * 60
            const y = Math.floor(x/60)
            x = Math.floor(x) - y *60
            return  y+ " : " + x
        }
        args.push('Thời gian ' + '= ' + foo(Number(cb_obj['x']).toFixed(2)));
        args.push('Giá ' + '= ' + Number(cb_obj['y']).toFixed(2));

        var line = "<span style=%r><b>"+ "</b>" + args.join(", ") + "</span>\\n";
        var text = line;
        var lines = text.split("\\n")
        if (lines.length > 3)
            lines.shift();
        div.text = lines.join("\\n");
    """ % (attributes, style))

def hookupFigure(p, display_event=display_event):
    div = Div(width=400, height=p.plot_height, height_policy="fixed")
    p.js_on_event(events.LODStart, display_event(div))  # Start of LOD display
    p.js_on_event(events.LODEnd, display_event(div))  # End of LOD display
    ## Events with attributes
    point_attributes = ['x', 'y']  # Point events
    point_events = [events.MouseMove, ]
    for event in point_events:
        p.js_on_event(event, display_event(div, attributes=point_attributes))
    return p, div

########################################################################################################################


def trimDataFrame(dic, KEYS=OHLC_KEYS):
    dic = copy(dic)
    dic['i'] = range(len(dic[KEYS[0]]))
    dd ={}
    for key in KEYS: dd[key] = []
    for i in range(0, MID):
        for key in KEYS: dd[key].append(dic[key][i])
    for i in range(AFTERNOON, END):
        for key in KEYS: dd[key].append(dic[key][i])

    return pd.DataFrame.from_dict(dd)


#####################################################################################################################
def experimentTimeDelta(): # This is a valid index for resampling !
    from pandas._libs.tslibs.timestamps import Timestamp
    from pandas import Timedelta, Series
    t = Timestamp('2020-10-29 09:00:00', freq='T')
    lst = []
    for i in range(5):
        lst.append(t)
        t += Timedelta('1 hour')
    for i in range(5):
        lst.append(t)
        t += Timedelta('2 hour')
    return Series(range(len(lst)), index=lst) # valid even though interval are irregular

# series = experimentTimeDelta()
def genOHCLpage():
    data, atc = parsePsOrder(fakeRequestPsData()['data'])
    priceSeries, volumeSeries = createDFfromOrderBook(data, DATE=DATE)
    df, dic, resampled = ohlcFromPrices(priceSeries, volumeSeries)
    ohlcPlot = plotPsTrimmed(trimDataFrame(dic))
    p, div = hookupFigure(ohlcPlot)
    return p, div

# p, div = genOHCLpage()
# output_file("candlestick_trimmed.html", title="candlestick.py example")
# show(column(p, div))
