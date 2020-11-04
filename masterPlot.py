import pandas as pd
from datetime import datetime
from bokeh.events import ButtonClick
from bokeh.document.document import Document
from bokeh.plotting import Figure, show, output_file
from bokeh.models import ColumnDataSource, Range1d, CrosshairTool, WheelZoomTool, CustomJS, Div, Button
from bokeh.layouts import column, row, layout
from ohlc29 import genOHCLpage
from dfManipulations import filterOutNonTradingTime, computeMinuteData, createColumnDataSource


import urllib.request, json
from bokeh.plotting import figure, curdoc

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
    pVolume = Figure(width=PLOT_WIDTH, height=VOLUME_PLOT_HEIGHT,  tools="pan, reset",
                     name="pltVolume")
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
    pBuySell = Figure(width=PLOT_WIDTH, height=BUYSELL_PLOT_HEIGHT,tools="pan, reset,ywheel_zoom , box_zoom",
                      name='pltBuySell')
    # pBuySell.y_range=Range1d()
    # p.axis[0].visible = False
    # pBuySell.y_range.end = Y_MAX

    wz = WheelZoomTool(dimensions="width"); pBuySell.add_tools(wz); pBuySell.toolbar.active_scroll = wz
    pBuySell.toolbar.logo = None

    pBuySell.line(x='index', y='buyPressure', source=source, color='green',
                  legend_label="Tổng đặt mua", name="glyphSellPressure")
    pBuySell.line(x='index', y='sellPressure', source=source, color='red',
                  legend_label="Tổng đặt bán", name="glyphBuyPressure")
    pBuySell.axis[0].visible = False
    pBuySell.legend.location = "top_left"
    pBuySell.legend.click_policy = "hide"
    pBuySell.legend.background_fill_alpha = 0.0

    return pBuySell

def update(doc: Document):
    dt = doc.get_model_by_name("divText")

    idf = fetchHoseIndicatorsData()
    psOrders, dfPsMinute = fetchPhaiSinhData()

    n = datetime.now()

    delta = (n.second + n.minute * 60 + n.hour * 3600) - psOrders[-1]['hour'] * 3600 - psOrders[-1]['minute'] * 60 - \
            psOrders[-1]['second']
    text = f"Số lượng Hose data point đã scraped được: <br/> {len(idf)}<br/>"
    text += f"Số order phái sinh đã match trong ngày: <br/>{len(psOrders)} <br/>"
    # text += f"Lần gần nhất cách đây {delta} giây <br/><br/>"
    text += f"Dư mua: {idf.iloc[-1]['buyPressure']:.2f} &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp"
    text += f"Dư bán: {idf.iloc[-1]['sellPressure']:.2f} <br/>"
    text += f"NN mua(total): {idf.iloc[-1]['nnBuy']:.2f} &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp"
    text += f"NN bán(total): {idf.iloc[-1]['nnSell']:.2f} <br/>"


    stamps = list(map(lambda x: x['stamp'], idf['time'].values))
    stamps = list(map(lambda x: datetime.fromtimestamp(int(x / 1000)), stamps))

    from copy import deepcopy
    idf['timeStamp'] = deepcopy(stamps)
    idf['stamp'] = deepcopy(stamps)
    idf = idf.set_index('stamp')


    ############################################ HOSE Indicators ############################################
    dfBuySell = filterOutNonTradingTime(idf[['buyPressure', 'sellPressure']])
    sourceBuySell = createColumnDataSource(dfBuySell)
    currentSource : ColumnDataSource = doc.get_model_by_name("glyphBuyPressure").data_source    #uphose
    recent = len(dfBuySell)
    oldCount = len(currentSource.data['buyPressure'])
    numHoseUpdates = recent - oldCount

    hoseUpdate = {key:sourceBuySell.data[key][oldCount: recent] for key in sourceBuySell.data.keys()}
    currentSource.stream(hoseUpdate)
    # currentSource.data['buyPressure'] += hoseupdate['buyPressure']
    # currentSource.data['sellPressure'] += hoseupdate['sellPressure']
    # currentSource.data['index'] += hoseupdate['index']
    # currentSource.stream(hoseupdate)

    text += f"<br/><br/>Số data-points mới cho HOSE chưa được cập nhật: <br/>{numHoseUpdates-1}<br/>"
    # currentSource.keys ['buyPressure', 'sellPressure', 'index']
    #hose

    ############################################### Ps Candles ##############################################
    psSource: ColumnDataSource = doc.get_model_by_name("glyphOHLCSegment").data_source
    nPSCandles = len(psSource.data['open'])
    nPSOrders = psSource.data['num'][0]
    nUnupdatedPSOrders = len(psOrders) - nPSOrders
    text += f"Số data-point mới cho Phái Sinh chưa được cập nhật: <br/> {len(dfPsMinute) - nPSCandles}<br/>"  # update
    if nUnupdatedPSOrders > 0:
        pass
    ############################################### Ps Pressure ##############################################
    if (datetime.now().hour*60 +  datetime.now().minute) > 14*60 + 30:
        dt.text = text
        return
    with urllib.request.urlopen("http://localhost:5001/ps-pressure-out") as url:
        data = json.loads(url.read().decode())
    data = data["psPressure"]
    text += f"psBuyPressure: &nbsp&nbsp{data['psBuyPressure']:.2f} <br/>psSellPressure:&nbsp&nbsp {data['psSellPressure']:.2f} <br/>"
    text += f"buyVolumes: {data['volBuys']} &nbsp&nbsp (total {data['totalVolBuys']}) <br/> "
    text += f"sellVolumes: {data['volSells']} &nbsp&nbsp (total {data['totalVolSells']}) <br/> "
    dt.text = text

def hookUpPlots(pCandle, pBuySell, pVolume, divCandle, divText, crosshairTool):
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

    def btnStart_clicked(event):
        btnStart._document.get_model_by_name("btnStart").label = "Started!"
        # activation_function()

    def activation_function():
        btnStart._document.add_periodic_callback(lambda: update(btnStart._document), 1000)
        btnStart._document.get_model_by_name("btnStart").label = "Started!"
        btnStart.disabled = True

    btnStart = Button(label="Start automatic update", button_type="success", name="btnStart")
    btnStart.on_event(ButtonClick, btnStart_clicked)
    return row(column(pCandle, pBuySell, pVolume), column(divCandle, btnStart, divText,)), activation_function

########################################################################################################################

def fetchHoseIndicatorsData():
    with urllib.request.urlopen("http://localhost:5000/api/hose-indicators-outbound") as url:
        data = json.loads(url.read().decode())
    return pd.DataFrame([dp for dp in data if dp is not None])


def fetchPhaiSinhData():
    from ohlc29 import ohlcFromPrices, createDFfromOrderBook
    import urllib.request, json
    from CONSTANT import DATE
    with urllib.request.urlopen("http://localhost:5001/ps-pressure-out") as url:
        data = json.loads(url.read().decode())  # ['orders', 'psPressure']

    rawData = data
    priceSeries, volumeSeries = createDFfromOrderBook(rawData['orders'], DATE)

    df, dic, resampled = ohlcFromPrices(priceSeries, volumeSeries)
    df = filterOutNonTradingTime(pd.DataFrame(dic).set_index("date"))

    return rawData['orders'], df


def makeMasterPlot():
    idf = fetchHoseIndicatorsData()
    stamps = list(map(lambda x: x['stamp'], idf['time'].values))
    stamps = list(map(lambda x: datetime.fromtimestamp(int(x/1000)), stamps))

    from copy import deepcopy
    idf['timeStamp'] = deepcopy(stamps)
    idf['stamp'] = deepcopy(stamps)
    idf = idf.set_index('stamp')

    dfVolume = filterOutNonTradingTime(computeMinuteData(idf, ['totalValue', 'nnBuy', 'nnSell']))
    sourceVolume = createColumnDataSource(dfVolume)
    pVolume = createVolumePlot(sourceVolume)

    dfBuySell = filterOutNonTradingTime(idf[['buyPressure', 'sellPressure']])
    sourceBuySell = createColumnDataSource(dfBuySell)
    pBuySell = createBuySellPlot(sourceBuySell)

    pCandle, divCandle = genOHCLpage(OHLC_PLOT_HEIGHT)
    divText = Div(width=400, height=500, height_policy="fixed", name="divText")
    dfVolume = filterOutNonTradingTime(computeMinuteData(idf, ['totalValue', 'nnBuy', 'nnSell']))
    sourceVolume = createColumnDataSource(dfVolume)
    pVolume = createVolumePlot(sourceVolume)

    dfBuySell = filterOutNonTradingTime(idf[['buyPressure', 'sellPressure']])
    sourceBuySell = createColumnDataSource(dfBuySell)
    pBuySell = createBuySellPlot(sourceBuySell)

    page = hookUpPlots(pCandle, pBuySell, pVolume, divCandle, divText,CrosshairTool(dimensions="both"))
    return page


#output_file("/tmp/foo.html"); page, activate = makeMasterPlot(); show(page)


# curdoc().add_root(page)
# OVER_TIME = True # TODO: Write smart back/front(scrape) code to avoid crashing when over time
