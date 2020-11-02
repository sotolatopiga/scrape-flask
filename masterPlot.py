import pandas as pd
from datetime import datetime
from commonOld import tik, tok
from bokeh.plotting import Figure, show, output_file
from bokeh.models import ColumnDataSource, Range1d, CrosshairTool, WheelZoomTool, CustomJS, Div
from bokeh.layouts import column, row, layout
from ohlc29 import genOHCLpage
from dfManipulations import filterOutNonTradingTime, computeMinuteData, createColumnDataSource
from dbIntegration import getIndicatorDF
from pandas import DataFrame

DEBUG = False
DBNAME = "mydb"
COLLECTION = "hosesnapshot"
PLOT_WIDTH = 1400
BUYSELL_PLOT_HEIGHT = 200
VOLUME_PLOT_HEIGHT = 130
OHLC_PLOT_HEIGHT = 530
LIQUIDITY_ALPHA = 0.4
BAR_WIDTH = 1
Y_MIN, Y_MAX = 0, 600


def createVolumePlot(source):
    pVolume = Figure(width=PLOT_WIDTH, height=VOLUME_PLOT_HEIGHT,  tools="pan, reset" )
    pVolume.toolbar.logo = None
    wz = WheelZoomTool(dimensions="height"); pVolume.add_tools(wz); pVolume.toolbar.active_scroll = wz

    pVolume.vbar(x='index', top='totalValue', width=BAR_WIDTH/60,source=source, color='blue', # HARDCODED
                 fill_alpha=LIQUIDITY_ALPHA , line_alpha=LIQUIDITY_ALPHA,
                 legend_label="Thanh khoản toàn tt", name="glyphLiquidity")
    pVolume.vbar(x='index', top='nnBuy', width=BAR_WIDTH/60,source=source, color='green',
                 legend_label="NN mua", name="glyphNNBuy")
    pVolume.vbar(x='index', top='nnSell', width=BAR_WIDTH/60,source=source, color='red',
                  legend_label="NN bán", name="glyphNNSell")

    pVolume.y_range=Range1d(-20, 65)
    pVolume.legend.location = "top_left"
    pVolume.legend.click_policy = "hide"
    pVolume.legend.background_fill_alpha = 0.0
    return pVolume


def createBuySellPlot(source):
    pBuySell = Figure(width=PLOT_WIDTH, height=BUYSELL_PLOT_HEIGHT,tools="pan, reset,ywheel_zoom , box_zoom" )
    pBuySell.y_range=Range1d()
    # p.axis[0].visible = False
    pBuySell.y_range.end = Y_MAX

    wz = WheelZoomTool(dimensions="width"); pBuySell.add_tools(wz); pBuySell.toolbar.active_scroll = wz
    pBuySell.toolbar.logo = None

    pBuySell.line(x='index', y='buyPressure', source=source, color='green',
                  legend_label="Tổng đặt mua", name="glyphBuyPressure")
    pBuySell.line(x='index', y='sellPressure', source=source, color='red',
                  legend_label="Tổng đặt bán", name="glyphBuyPressure")
    pBuySell.axis[0].visible = False
    pBuySell.legend.location = "top_left"
    pBuySell.legend.click_policy = "hide"
    pBuySell.legend.background_fill_alpha = 0.0

    return pBuySell


def hookUpPlots(pCandle, pBuySell, pVolume, divCandle, crosshairTool):
    pCandle.x_range = pBuySell.x_range
    pVolume.x_range = pBuySell.x_range
    pCandle.add_tools(crosshairTool)
    pBuySell.add_tools(crosshairTool)
    pVolume.add_tools(crosshairTool)
    pCandle.xaxis.ticker = [8.75, 9, 9.5, 10, 10.5, 11, 11.5, 13, 13.5, 14, 14.5, 14.75]
    pCandle.xaxis.major_label_overrides = {
        8.5:"8:30", 8.75:"8:45", 9:"9:00", 9.5:"9:30", 10:"10:00",
        10.5:"10:30", 11:"11:00", 11.5:"11:30", 13:"13:00",
        13.5:"13:30", 14:"14:00", 14.5:"14:30", 14.75:"14:45"}
    pBuySell.xaxis.ticker = pCandle.xaxis.ticker
    pVolume.xaxis.ticker = pCandle.xaxis.ticker
    pVolume.xaxis.major_label_overrides = pCandle.xaxis.major_label_overrides
    return row(column(pCandle, pBuySell, pVolume), divCandle)

########################################################################################################################


idf = getIndicatorDF()

dfVolume = filterOutNonTradingTime(computeMinuteData(idf, ['totalValue', 'nnBuy', 'nnSell']))
sourceVolume = createColumnDataSource(dfVolume)
pVolume = createVolumePlot(sourceVolume)

dfBuySell = filterOutNonTradingTime(idf[['buyPressure', 'sellPressure']])
sourceBuySell = createColumnDataSource(dfBuySell)
pBuySell = createBuySellPlot(sourceBuySell)

pCandle, divCandle = genOHCLpage(OHLC_PLOT_HEIGHT)

page = hookUpPlots(pCandle, pBuySell, pVolume, divCandle, CrosshairTool(dimensions="both"))
show(page)
