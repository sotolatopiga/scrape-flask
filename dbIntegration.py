from pymongo import MongoClient
import pandas as pd
from dataLoader import initializeData, getDataObject
from datetime import datetime
from commonOld import tik, tok
from bokeh.plotting import Figure, show, output_file
from bokeh.models import ColumnDataSource, Range1d, CrosshairTool, WheelZoomTool, CustomJS, Div
from bokeh.layouts import column
DBNAME = "mydb"
COLLECTION = "hosesnapshot"
PLOT_WIDTH = 1400


DB_URI = "mongodb://sotola:na6pi3pi@13.212.108.204/?authSource=admin"

def getIndicatorsDB(db_name="test1", collection_name="indicators"):
    db = _client[db_name]
    col = db[collection_name]
    d = list(col.find())
    df =pd.DataFrame.from_dict(d)
    return df

_client = MongoClient( DB_URI)
#%%
tik()
initializeData()
tok()
#%%


# ['_id', 'times', 'indicators', 'hour', 'time', 'value']
tik()
df2 = getIndicatorsDB()
tok()
df2.tail()


#%%





#%%

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

# dumpIndicatorsToDB(getDataObject())

idf = getIndicatorsDB()     # ['snapshots', 'times', 'parsed', 'indicators']
# ['time', 'buyPressure', 'sellPressure', 'nnBuy', 'nnSell', 'totalValue', 'i'] + 'stamp'
INDICATOR_KEYS = ['time', 'buyPressure', 'sellPressure', 'nnBuy', 'nnSell', 'totalValue', 'i']
for key in INDICATOR_KEYS:
    idf[key] = idf['indicators'].map(lambda x: x[key])

tdf = idf.set_index('stamp')

tdf['foo'] = tdf['totalValue'].diff(1)


p = Figure(width=PLOT_WIDTH)
tdf['stamp'] = idf['stamp']
dic = dict(stamp=idf['stamp'].values, foo=tdf['foo'].values)
p.vbar(x='i', top='foo', width=10, source=ColumnDataSource(tdf[['i', 'foo']]))
output_file("/tmp/foo.html")
p.y_range=Range1d(-10, 10, bounds='auto')
show(p)
#%%
idf = getIndicatorsDB().set_index('stamp') # ['snapshots', 'times', 'parsed', 'indicators']

INDICATOR_KEYS = ['time', 'buyPressure', 'sellPressure', 'nnBuy', 'nnSell', 'totalValue', 'i']
for key in INDICATOR_KEYS:
    idf[key] = idf['indicators'].map(lambda x: x[key])

ddf = idf[['totalValue', 'nnBuy', 'nnSell']].diff(1).resample('1Min').agg(sum)

ddf['nnSell'] = ddf['nnSell'] * -1

# ddf = ddf.resample('1S').agg(sum)
# ddf = ddf.fillna('ffill')  # Doesnt work because there's no Nan
ddf['x'] = range(len(ddf))
source = ColumnDataSource(ddf)

pVolume = Figure(width=PLOT_WIDTH, height=200)
LIQUIDITY_ALPHA = 0.4
pVolume.vbar(x='x', top='totalValue', width=1,source=source, color='blue', # HARDCODED
       fill_alpha=LIQUIDITY_ALPHA , line_alpha=LIQUIDITY_ALPHA )
pVolume.vbar(x='x', top='nnBuy', width=0.5,source=source, color='green')
pVolume.vbar(x='x', top='nnSell', width=0.5,source=source, color='red')
pVolume.y_range=Range1d(-20, 65)
#output_file("/tmp/foo.html")
#show(pVolume)

Y_MIN = 0; Y_MAX = 500
DOWN_SHIFT = 50
DELTA_SCALE = 10; DELTA_STEP = 1
p = Figure( width=PLOT_WIDTH, height=550,) #y_range=(Y_MIN, Y_MAX)

p.y_range=Range1d(Y_MIN, Y_MAX, bounds='auto')
# p.axis[0].visible = False
p.y_range.end = Y_MAX
crosshairTool = CrosshairTool(dimensions="both")
p.add_tools(crosshairTool)
wheel_zoom = WheelZoomTool()
p.add_tools(wheel_zoom)
p.toolbar.active_scroll = wheel_zoom
p.toolbar.logo = None

idf['i'] /= 60
source = ColumnDataSource(idf[INDICATOR_KEYS])

p.line(x='i', y='buyPressure', source=source, color='green')
p.line(x='i', y='sellPressure', source=source, color='red')
pVolume.x_range = p.x_range
pVolume.add_tools(crosshairTool)
output_file("/tmp/foo.html")
show(column(p, pVolume))
#%%
p = Figure(width=PLOT_WIDTH)
p.line(range(len(idf)), idf['buyPressure'].values, color='red')
p.line(range(len(idf)), idf['sellPressure'].values, color='blue')
show(p)