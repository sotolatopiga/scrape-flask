from functools import reduce

BILLION = 1000000000

class C:
    COL_GIA3 = 3
    COL_VOL3 = 4
    COL_GIA2 = 5
    COL_VOL2 = 6
    COL_GIA1 = 7
    COL_VOL1 = 8

    COL_GIA = 9
    COL_VOL = 10

    COL_GIA1b = 12
    COL_VOL1b = 13
    COL_GIA2b = 14
    COL_VOL2b = 15
    COL_GIA3b = 16
    COL_VOL3b = 17
    COL_TOTAL_VOL = 18
    COL_AVG_PRICE = 21
    COL_HIGH = 22
    COL_LOW = 23
    NN_BUY = 24
    NN_SELL = 25

    DATA_2_PLOT_RATIO = 100000

    CTIME = "times"
    CBUYP = "buyPressure"
    CSELLP = "sellPressure"
    CHOSE="hoseSnapShot"
    LOCAL="local"


def parsePrice(x):
    if x.replace(".", "").isnumeric(): return float(x)
    return 0


def parseVol(x):
    x = x.replace(",", "")
    if x.isnumeric(): return int(x)
    return 0


def parseHose(data):
    dic = {}
    def parseRow(row):
        raw = row[1:]
        raw[C.COL_GIA1] = parsePrice(raw[C.COL_GIA1]) * 1000
        raw[C.COL_GIA2] = parsePrice(raw[C.COL_GIA2]) * 1000
        raw[C.COL_GIA3] = parsePrice(raw[C.COL_GIA3]) * 1000
        raw[C.COL_VOL1] = parseVol(raw[C.COL_VOL1]) * 10
        raw[C.COL_VOL2] = parseVol(raw[C.COL_VOL2]) * 10
        raw[C.COL_VOL3] = parseVol(raw[C.COL_VOL3]) * 10
        raw[C.COL_GIA1b] = parsePrice(raw[C.COL_GIA1b]) * 1000
        raw[C.COL_GIA2b] = parsePrice(raw[C.COL_GIA2b]) * 1000
        raw[C.COL_GIA3b] = parsePrice(raw[C.COL_GIA3b]) * 1000
        raw[C.COL_VOL1b] = parseVol(raw[C.COL_VOL1b]) * 10
        raw[C.COL_VOL2b] = parseVol(raw[C.COL_VOL2b]) * 10
        raw[C.COL_VOL3b] = parseVol(raw[C.COL_VOL3b]) * 10
        raw[C.COL_GIA] = parseVol(raw[C.COL_GIA]) * 1000
        raw[C.COL_VOL] = parseVol(raw[C.COL_VOL]) * 10
        raw[C.COL_TOTAL_VOL] = parseVol(raw[C.COL_TOTAL_VOL]) * 10
        raw[C.COL_AVG_PRICE] = parsePrice(raw[C.COL_AVG_PRICE])  * 1000
        raw[C.COL_HIGH] = parsePrice(raw[C.COL_HIGH])  * 1000
        raw[C.COL_LOW] = parsePrice(raw[C.COL_LOW])  * 1000
        raw[C.NN_SELL] = parseVol(raw[C.NN_SELL]) * 10
        raw[C.NN_BUY] = parseVol(raw[C.NN_BUY]) * 10
        dic[row[0]] = raw
    list(map(parseRow, data))
    return dic


def sellPressure(hose):
    def stockSellPressure(stock):
        data = hose[stock]
        return data[C.COL_VOL1b] * data[C.COL_GIA1b] + \
               data[C.COL_VOL2b] * data[C.COL_GIA2b] + \
               data[C.COL_VOL3b] * data[C.COL_GIA3b]
    return reduce(lambda a, b: a + b, map(stockSellPressure, hose)) / BILLION


def buyPressure(hose):
    def stockBuyPressure(stock):
        data = hose[stock]
        return data[C.COL_VOL1] * data[C.COL_GIA1] + \
               data[C.COL_VOL2] * data[C.COL_GIA2] + \
               data[C.COL_VOL3] * data[C.COL_GIA3]
    return reduce(lambda a, b: a + b, map(stockBuyPressure, hose)) / BILLION


def totalValue(hose):
    def stockValue(stock):
        data = hose[stock]
        return data[C.COL_AVG_PRICE] * data[C.COL_TOTAL_VOL]
    return reduce(lambda a, b: a + b, map(stockValue, hose)) / BILLION


def nnBuy(hose):
    def buy(stock):
        data = hose[stock]
        return data[C.COL_AVG_PRICE] * data[C.NN_BUY]
    return reduce(lambda a, b: a + b, map(buy, hose)) / BILLION


def nnSell(hose):
    def sell(stock):
        data = hose[stock]
        return data[C.COL_AVG_PRICE] * data[C.NN_SELL]
    return reduce(lambda a, b: a + b, map(sell, hose)) / BILLION


def computeIndicators(hose, time):
    dic = {'time': time,
            'buyPressure': buyPressure(hose), 'sellPressure': sellPressure(hose),
           'nnBuy':nnBuy(hose), 'nnSell':nnSell(hose), "totalValue": totalValue(hose),}
    return dic


def getIndicators(data):
    def foo(snapShot):
        t  = snapShot['time']
        time = (t['hour'] * 3600 + 60.0*t['minute'] + t['minute']) / 3600.0
        indicators = computeIndicators(snapShot['parsed'], time)
        indicators['time'] = time
        return indicators
    # a = mmap(computeIndicators, da
    # ta['parsed'])
    return list(map(foo, data))