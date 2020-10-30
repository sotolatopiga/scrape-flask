import pandas as pd, numpy as np, pickle, json
from collections import OrderedDict

MARKET_START = 9 # MUST edit if not int. e.g 8.45 change date string below
MARKET_STARTS = int(MARKET_START * 3600)
MARKET_END = 14.75
MARKET_ENDS = int(MARKET_END *3600 + 60)
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


def ohlcFromPrices(dfPrice, sample='1Min'):
    df = dfPrice.resample(sample).agg(  # series.resample('60s')
        OrderedDict([
            ('open', 'first'),
            ('high', 'max'),
            ('low', 'min'),
            ('close', 'last'),]))
    dic = {}
    for key in ['open', 'high', 'low', 'close']:
        dic[key] = df[key].fillna(method='pad').values
    dic['index'] = list(map(lambda x: x[1], df.index[:len(df['open'])]))
    df = pd.DataFrame.from_dict(dic).set_index('index')
    return df

##################################################################################################################

dfPrice, dfVolume = createDFfromOrderBook(
                        parsePsOrder(fakeRequestPsData()['data']))
ohlcFromPrices(dfPrice)


