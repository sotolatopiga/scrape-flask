from bokeh.server.server import Server
from bokeh.util.browser import view
from bokeh.document.document import Document
from bokeh.application.handlers import FunctionHandler
from bokeh.application.application import  Application
from bokehNotebook import createDocument

from masterPlot import makeMasterPlot, fetchPhaiSinhData, fetchHoseIndicatorsData


def threading_func_wrapper(func, delay=0.001, args=None, start=True):
    import threading
    if args is None:
        func_thread = threading.Timer(delay, func)
    else:
        func_thread = threading.Timer(delay, func, (args,))
    if start: func_thread.start()
    return func_thread


def attachDocToServer(doc : Document):
    global _docs
    # doc.add_root(_page)
    page, activation_function = makeMasterPlot()
    doc.add_root(page)
    activation_function()
    # "glyphBuyPressure"
    # "glyphNNBuy"
    # "glyphGreenOHLC"
    # "divText"
    # "divCustomJS"
    doc.get_model_by_name("divText")
    _docs.append(doc)

if "servers" not in globals(): servers = []

_docs = []
BOKEH_PORT = 5008


if len(servers) > 0:
    print("Stopping old server...")
    servers[-1].io_loop.stop()
    servers[-1].stop()

s  = Server({'/' : Application(FunctionHandler(attachDocToServer))},
            num_proc=16,
            port=BOKEH_PORT,
            allow_websocket_origin=["*"])

s.start()
servers.append(s)
view(f"http://localhost:{BOKEH_PORT}")
threading_func_wrapper(s.io_loop.start, delay=0.001)


doc = None
def dummy():
    global _docs, doc
    #########################################################################################################################
    _docs[-1].get_model_by_name("glyphBuyPressure").data_source.data.keys() # ['buyPressure', 'sellPressure', 'index']
    _docs[-1].get_model_by_name("glyphNNBuy").data_source.data.keys() # ['totalValue', 'nnBuy', 'nnSell', 'timeStamp', 'index']
    _docs[-1].get_model_by_name("glyphOHLCSegment").data_source.data.keys() # ['open', 'high', 'low', 'close', 'vol', 'redCandleAlpha', 'index']
    doc = _docs[-1]

threading_func_wrapper(dummy, 4)