from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from commonOld import tik, tok
from bokeh.plotting import Figure, show, output_file
from bokeh.models import ColumnDataSource, Range1d, CrosshairTool, WheelZoomTool, CustomJS, Div
from bokeh.layouts import column, row, layout
from ohlc29 import genOHCLpage
from copy import copy


DEBUG = False
DBNAME = "mydb"
COLLECTION = "hosesnapshot"

DB_URI = "mongodb://sotola:na6pi3pi@13.212.108.204/?authSource=admin"


def dumpIndicatorsToDB(dataObject):
    df = pd.DataFrame.from_dict(dataObject._dic)
    df['seconds'] = df['times'].map(timeStr2Time)
    df['stamp'] =  df['times'].map(lambda x: datetime.fromtimestamp(x['stamp']/1000))

    col = _client["test1"]["indicators"]
    tik()
    col.insert_many(df[['seconds', 'indicators', 'stamp']].to_dict("records"))
    tok()


def getRawIndicatorsFromDB(db_name="test1", collection_name="indicators"):
    db = _client[db_name]
    col = db[collection_name]
    d = list(col.find())
    df =pd.DataFrame.from_dict(d)
    return df


def getIndicatorDF():
    idf = getRawIndicatorsFromDB()  # idf.keys =  ['seconds', 'indicators', 'stamp']

    idf['timeStamp'] = copy(idf['stamp'])
    idf = idf.set_index('stamp')

    INDICATOR_KEYS = ['time', 'buyPressure', 'sellPressure', 'nnBuy', 'nnSell', 'totalValue', 'i']
    # ['seconds', 'indicators', 'timeStamp', 'time', 'buyPressure','sellPressure', 'nnBuy', 'nnSell', 'totalValue', 'i']
    for key in INDICATOR_KEYS:
        idf[key] = idf['indicators'].map(lambda x: x[key])
    return idf


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

_client = MongoClient(DB_URI)