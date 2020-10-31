from random import random

from bokeh.layouts import column
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
from bokeh.server.server import Server
from bokeh.util.browser import view
from bokeh.application.handlers import FunctionHandler
from bokeh.application.application import  Application
from bokehNotebook import createDocument


def threading_func_wrapper(func, delay=0.5, args=None, start=True):
    import threading
    if args is None:
        func_thread = threading.Timer(delay, func)
    else:
        func_thread = threading.Timer(delay, func, (args,))
    if start: func_thread.start()
    return func_thread


def attachDocToServer(doc):
    global _docs
    doc.add_root(createDocument())
    _docs.append(doc)


_docs = []
_dic = {}
#%%
BOKEH_PORT = 5008
if 's' in globals():
    _dic['server'].io_loop.stop();
    _dic['server'].stop()

s  = Server({'/' : Application(FunctionHandler(attachDocToServer))},
            num_proc=4,
            port=BOKEH_PORT,
            allow_websocket_origin=["*"])
s.start()
_dic['server'] = s
view(f"http://localhost:{BOKEH_PORT}")
threading_func_wrapper(s.io_loop.start, delay=0.001)