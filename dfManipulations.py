import pandas as pd
from pandas import Timestamp, DataFrame
from bokeh.models import ColumnDataSource

DEBUG = False


def filterOutNonTradingTime(df, num=None):
    def isValid(t):
        return start <= t <= lunch or noon <= t <= end
    start = pd.Timestamp(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day, hour=9, minute=0, freq='T')
    lunch = pd.Timestamp(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day, hour=11, minute=29, freq='T')
    noon = pd.Timestamp(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day, hour=13, minute=0, freq='T')
    end = pd.Timestamp(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day, hour=14, minute=45, freq='T')
    # return [t for t in df.index if isValid(t)]
    # return [ start <= df.index]
    if num is not None: df['num'] = [num] * len(df)
    res = df[list(map(isValid, df.index))]

    return res


def computeMinuteData(idf, lst):
    _ddf = idf[lst].diff(1).resample('1Min').agg(sum)
    _ddf['nnSell'] = _ddf['nnSell'] * -1
    _ddf['timeStamp'] = idf['timeStamp'].resample('1Min').agg('first').values
    if DEBUG: print(_ddf[100:129])
    return _ddf


def createColumnDataSource(ddf):
    dic = {key: ddf[key].values for key in ddf.columns}
    dic['index'] = list(map(lambda t: (t.hour * 3600 + t.minute * 60 + t.second) / 3600, ddf.index))
    source = ColumnDataSource(dic)
    return source