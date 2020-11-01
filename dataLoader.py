import pickle, json
from copy import copy
from hoseParser import computeIndicators
from bokeh.models import Span, CrosshairTool, HoverTool, ResetTool, PanTool
from bokeh.models import WheelZoomTool, ColumnDataSource, Button, CustomJS, Div
from CONSTANT import *
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
from math import pi

"""
const obj = {
    time: {
        hour:9,
        minute:10,
        second:10,
    },
    parsed:{
        'AAA': {
            gia1: 100,
            volume1: 1230
        },
        'AAM':{
            gia1: 100,
            volume1: 200
        }
    }
}

pickled = [obj, obj, obj,]
"""


def loadData_29():
    with open('data/data.29_Oct-(150)_morning.pickle', "rb") as file:
        parsed = pickle.load(file)
        hoseSnapshots = list(map(lambda x: x['parsed'], parsed))
        timeSnapshotTaken = list(map(lambda x: x['time'], parsed))

    with open('data/data.29_Oct-(150)_afternoon.pickle.', "rb") as file:
        data2 = pickle.load(file)
        hoseSnapshots += list(map(lambda x: x['parsed'], data2))
        timeSnapshotTaken += list(map(lambda x: x['time'], data2))
        parsed += data2

    indicators = computeIndicators(parsed)
    return hoseSnapshots, timeSnapshotTaken, parsed, indicators


def convertToStream(snapshots, times):
    import pickle , dictdiffer
    lst = []

    for i in range(1, len(snapshots)):
        print(f"\rsnapshot #{i}/{len(snapshots)}: calculating differences", end="")
        lst.append({
            'time': times[i],
            'delta': list(dictdiffer.diff(snapshots[i], snapshots[i - 1]))})

    with open("HOSE-stream.pickle", "wb") as file:
        pickle.dump({"start": snapshots[0], "steps":lst}, file)


def cacheDataToDisk():
    CACHED = ["times", "indicators"]
    print("Dumping to file:")
    with open(CACHE_FILE_NAME.replace("DATE", "29"), "w") as file:
        json.dump({key:_o._dic[key] for key in CACHED}, file)


def createIndicatorDF(orders, DATE, MARKET_DURATION=MARKET_DURATION): # TODO: change Date to 1 of
    b = [None] * MARKET_DURATION         # TODO: Merge this with the orther CreateDF...
    s = [None] * MARKET_DURATION
    for order in orders:
        if order['i'] < MARKET_DURATION:
            b[order['i']] = order['buyPressure']
            s[order['i']] = order['sellPressure']

    index = pd.date_range(f'{DATE} 09:00:00',
                            periods=MARKET_DURATION, freq='S')
    return pd.Series(b, index=index), pd.Series(s, index=index)


def display_event_bs(div):
    return CustomJS(args=dict(div=div), code=""" 
        let args = [];
        const foo = (x, plot, doc, root) => {
            // console.clear()
            console.log([x, plot, doc, root]) // temp1[2].get_model_by_name("glypBuyPressure")
            let t = new Date(x.x - 3600 * 1000 * 7)
            
            return (""+t).split(" ").slice(0, -3).join(" ")
        }
        args.push('Thời gian ' + '= ' + foo(cb_obj, cb_obj.origin, cb_obj.origin.document, cb_obj.origin.document.roots()[0]));
        args.push('Giá ' + '= ' + Number(cb_obj['y']).toFixed(2));
    
        let line = "<span style='float:left;clear:left;font_size=13px'><b>"+ "</b>" + args.join(", ") + "</span>\\n";
        div.text = line // args=dict(div=div)
    """)


def hookupFigure(p, display_event=display_event_bs):
    from bokeh import events
    from bokeh.layouts import layout, column, row
    div = Div(width=400, height=p.plot_height, height_policy="fixed", name="divDisplay")
    page = column(p, div)
    p.js_on_event(events.LODStart, display_event(div))  # Start of LOD display
    p.js_on_event(events.LODEnd, display_event(div))  # End of LOD display

    point_events = [events.MouseMove,]
    for event in point_events:
        p.js_on_event(event, display_event(div))

    p.add_tools(CrosshairTool(dimensions="both"))
    wheel_zoom = WheelZoomTool()
    p.add_tools(wheel_zoom)
    p.toolbar.active_scroll = wheel_zoom
    return page

class DataWrapper:
    def __init__(self):
        self._dic = {"snapshots": (loadData_29())[0], "times": (loadData_29())[1], "parsed": (loadData_29())[2],
                     "indicators": (loadData_29())[3]}
        self.snapshots, self.times, self.parsed, self.indicators = self._dic["snapshots"], self._dic["times"], \
                                                                   self._dic["parsed"], self._dic["indicators"]


def initializeData(verbose=False):
    global _o
    assert _o is None
    if verbose: print("Reading data:")
    _o = DataWrapper()
    if verbose: print(len(_o.times))

def getDataObject():
    assert _o is not None, "Dataloader.py error: o has not been initialized"
    return _o

def genWebApp(display=False):
    if _o is None: initializeData()
    assert _o is not None, "Dataloader.py error: o has not been initialized"
    buys, sells = createIndicatorDF(_o.indicators, DATE)
    sells = sells.fillna(method='ffill').replace(np.nan, 0)
    buys = buys.fillna(method='ffill').replace(np.nan, 0)
    source = ColumnDataSource(dict(date=buys.index, buys=buys.values, sells=sells.values))

    p = figure(x_axis_type="datetime", plot_width=1600, title="HOSE buy/sell pressures",
               name="pltBuySell", tools="pan,box_zoom,reset,save")
    p.line('date', 'buys', source=source, color='green', legend_label="Tổng đặt mua", name="glypBuyPressure")
    p.line('date', 'sells', source=source, color='red',  legend_label="Tổng đặt bán", name="glypSellPressure")
    p.legend.location = "top_left"
    p.legend.click_policy="hide"

    p.xaxis.major_label_orientation = pi / 2
    p.grid.grid_line_alpha = 0.3

    page = hookupFigure(p, display_event=display_event_bs)
    if display:
        output_file("whatever.html")
        show(page)
    return page

_o = None
