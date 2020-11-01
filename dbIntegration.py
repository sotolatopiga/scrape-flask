from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from commonOld import tik, tok
from bokeh.plotting import Figure, show, output_file
from bokeh.models import ColumnDataSource, Range1d, CrosshairTool, WheelZoomTool, CustomJS, Div
from bokeh.layouts import column, row, layout
from ohlc import genOHCLpage
from copy import copy
from dfManipulations import filterOutNonTradingTime, computeMinuteData, createColumnDataSource
from pandas import DataFrame

DEBUG = False
DBNAME = "mydb"
COLLECTION = "hosesnapshot"
PLOT_WIDTH = 1500
BUYSELL_PLOT_HEIGHT = 200
VOLUME_PLOT_HEIGHT = 150
LIQUIDITY_ALPHA = 0.4
BAR_WIDTH = 1
Y_MIN, Y_MAX = 0, 600
DB_URI = "mongodb://sotola:na6pi3pi@13.212.108.204/?authSource=admin"


def getRawIndicatorsFromDB(db_name="test1", collection_name="indicators"):
    db = _client[db_name]
    col = db[collection_name]
    d = list(col.find())
    df =pd.DataFrame.from_dict(d)
    return df


def timeStr2Time(dp, second=True, hour=False, normalize = True):
    assert second or hour, "dbIntegration assertion error: must choose either second or hour"
    h, m, s = list(map(int, dp['time'].split('_')))
    total = h * 3600 + 60 * m + s
    if normalize: total -= 3600 * 9
    if second: return total
    if hour: return total / 3600
    """
    {   'day': '29',
        'month': '10',
        'year': 2020,
        'hour': 9,
        'minute': 11,
        'second': 8,
        'stamp': 1603937468744,
        'date': '2020_10_29',
        'time': '09_11_08',
        'datetime': '2020_10_29_09_11_08' }

    arr = getDataObject()._dic["times"]
    arr[0]['datetime']
    datetime.fromtimestamp(arr[0]['stamp']/1000)
    print(arr[0]['time']) => '09_11_08'
    """


def dumpIndicatorsToDB(dataObject):
    df = pd.DataFrame.from_dict(dataObject._dic)
    df['seconds'] = df['times'].map(timeStr2Time)
    df['stamp'] =  df['times'].map(lambda x: datetime.fromtimestamp(x['stamp']/1000))

    col = _client["test1"]["indicators"]
    tik()
    col.insert_many(df[['seconds', 'indicators', 'stamp']].to_dict("records"))
    tok()


_client = MongoClient( DB_URI)

#%%
idf = getRawIndicatorsFromDB()  # idf.keys =  ['seconds', 'indicators', 'stamp']


idf['timeStamp'] = copy(idf['stamp'])
idf = idf.set_index('stamp')

INDICATOR_KEYS = ['time', 'buyPressure', 'sellPressure', 'nnBuy', 'nnSell', 'totalValue', 'i']
# ['seconds', 'indicators', 'timeStamp', 'time', 'buyPressure','sellPressure', 'nnBuy', 'nnSell', 'totalValue', 'i']
for key in INDICATOR_KEYS:
    idf[key] = idf['indicators'].map(lambda x: x[key])



def createVolumePlot(source):
    pVolume = Figure(width=PLOT_WIDTH, height=VOLUME_PLOT_HEIGHT,  tools="pan, reset" )
    pVolume.toolbar.logo = None
    wz = WheelZoomTool(dimensions="width"); pVolume.add_tools(wz); pVolume.toolbar.active_scroll = wz

    pVolume.vbar(x='index', top='totalValue', width=BAR_WIDTH/60,source=source, color='blue', # HARDCODED
           fill_alpha=LIQUIDITY_ALPHA , line_alpha=LIQUIDITY_ALPHA,)
    pVolume.vbar(x='index', top='nnBuy', width=BAR_WIDTH/60,source=source, color='green')
    pVolume.vbar(x='index', top='nnSell', width=BAR_WIDTH/60,source=source, color='red')
    pVolume.y_range=Range1d(-20, 65)
    return pVolume


def createBuySellPlot(source):
    pBuySell = Figure(width=PLOT_WIDTH, height=BUYSELL_PLOT_HEIGHT,tools="pan, reset, save, box_zoom" )
    pBuySell.y_range=Range1d()
    # p.axis[0].visible = False
    pBuySell.y_range.end = Y_MAX

    wz = WheelZoomTool(dimensions="height"); pBuySell.add_tools(wz); pBuySell.toolbar.active_scroll = wz
    pBuySell.toolbar.logo = None

    pBuySell.line(x='index', y='buyPressure', source=source, color='green')
    pBuySell.line(x='index', y='sellPressure', source=source, color='red')
    pBuySell.axis[0].visible = False
    return pBuySell


def hookUpPlots(pVolume, pBuySell, crosshairTool):
    pVolume.x_range = pBuySell.x_range
    pVolume.add_tools(crosshairTool)
    pBuySell.add_tools(crosshairTool)

########################################################################################################################

dfVolume = filterOutNonTradingTime(computeMinuteData(idf, ['totalValue', 'nnBuy', 'nnSell']))
sourceVolume = createColumnDataSource(dfVolume)
pVolume = createVolumePlot(sourceVolume)

dfBuySell = filterOutNonTradingTime(idf[['buyPressure', 'sellPressure']])
sourceBuySell = createColumnDataSource(dfBuySell)
pBuySell = createBuySellPlot(sourceBuySell)

hookUpPlots(pVolume, pBuySell, CrosshairTool(dimensions="both"))
show(column(pBuySell, pVolume))
