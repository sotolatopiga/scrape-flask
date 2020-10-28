import os, pickle, json
from os import listdir
from os.path import isfile, join
from functools import reduce
from common import *
from random import random
import pandas as pd


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
    mmap(parseRow, data)
    return dic


def sellPressure(hose):
    def stockSellPressure(stock):
        data = hose[stock]
        return data[C.COL_VOL1b] * data[C.COL_GIA1b] + \
               data[C.COL_VOL2b] * data[C.COL_GIA2b] + \
               data[C.COL_VOL3b] * data[C.COL_GIA3b]
    return reduce(lambda a, b: a + b, map(stockSellPressure, hose))


def buyPressure(hose):
    def stockBuyPressure(stock):
        data = hose[stock]
        return data[C.COL_VOL1] * data[C.COL_GIA1] + \
               data[C.COL_VOL2] * data[C.COL_GIA2] + \
               data[C.COL_VOL3] * data[C.COL_GIA3]
    return reduce(lambda a, b: a + b, map(stockBuyPressure, hose))


def totalValue(hose):
    def stockValue(stock):
        data = hose[stock]
        return data[C.COL_AVG_PRICE] * data[C.COL_TOTAL_VOL]
    return reduce(lambda a, b: a + b, map(stockValue, hose))


def nnBuy(hose):
    def buy(stock):
        data = hose[stock]
        return data[C.COL_AVG_PRICE] * data[C.NN_BUY]
    return reduce(lambda a, b: a + b, map(buy, hose))


def nnSell(hose):
    def sell(stock):
        data = hose[stock]
        return data[C.COL_AVG_PRICE] * data[C.NN_SELL]
    return reduce(lambda a, b: a + b, map(sell, hose))


def compute(hose):
    dic = {'buyPressure': buyPressure(hose), 'sellPressure': sellPressure(hose),
           'nnBuy':nnBuy(hose), 'nnSell':nnSell(hose), "totalValue": totalValue(hose),}
    return dic