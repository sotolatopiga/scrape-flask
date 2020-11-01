from bokeh.server.server import Server
from bokeh.util.browser import view
from bokeh.application.handlers import FunctionHandler
from bokeh.application.application import  Application
from bokehNotebook import createDocument


def threading_func_wrapper(func, delay=0.001, args=None, start=True):
    import threading
    if args is None:
        func_thread = threading.Timer(delay, func)
    else:
        func_thread = threading.Timer(delay, func, (args,))
    if start: func_thread.start()
    return func_thread


def attachDocToServer(doc):
    global _docs, _page
    # doc.add_root(_page)
    doc.add_root(createDocument())
    _docs.append(doc)


_docs = []
_dic = {'servers':[]}
from dataLoader import page as _page
#%%
BOKEH_PORT = 5008

if len(_dic['servers']) > 0:
    _dic['servers'][-1].io_loop.stop()
    _dic['servers'][-1].stop()

s  = Server({'/' : Application(FunctionHandler(attachDocToServer))},
            num_proc=1,
            port=BOKEH_PORT,
            allow_websocket_origin=["*"])

s.start()
_dic['servers'] += [s]
view(f"http://localhost:{BOKEH_PORT}")
threading_func_wrapper(s.io_loop.start, delay=0.001)