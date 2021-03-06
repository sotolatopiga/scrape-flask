from Test import loadData_2020_10_28
from flask import Flask, jsonify, request
from flask_cors import CORS
from common import mmap, dump, threading_func_wrapper
from Context import Context
import json, pickle
from werkzeug.serving import run_simple
from requestHandler import handleHoseDataPost, OLD_HandlePsDataPost, handlePsDataGet, handleHoseDataGet
from DB_CONSTANTS import db


app = Flask(__name__)
CORS(app)

############################################# STATIC HTML PAGES ###################################################

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# Shut down server via http
@app.route("/shutdown")
def shutdown():
    shutdown_server()
    return "Successfully closed server"


# Home page
@app.route('/')
def index():
    a = {'name': 'Sarah', 'age': 34, 'isEmployed': True}
    return json.dumps(a)


########################################## OUTBOUND DATA SERVICES ###########################################

# Return hose indicators for charts
@app.route('/api/hose-indicators-outbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hose_indicators_outbound():
    return handleHoseDataGet(_o)


# Return phai sinh OHLC data for charts
@app.route('/api/ps-ohlc-outbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def ps_ohlc_outbound():
    return handlePsDataGet(_o)

########################################### INBOUND INGESTION ################################################

# Ingest phai sinh data
@app.route('/api/old-ps-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def OLD_ps_snapshot_inbound():
    return jsonify(OLD_HandlePsDataPost(_o))


@app.route('/api/ps-orders-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def ps_orders_inbound():
    orders, marketDepth = request.get_json()
    if len(_o.psHistory) < len(orders):
        _o.psHistory = list(reversed(orders))
    return {"msg":f"got {len(orders)} datapoints for ps Order & {len(marketDepth[0])} for marketDepth"}


# Ingest Hose data
@app.route('/api/hose-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hose_snapshot_inbound():
    timeObj, timeStr, data, indicators = handleHoseDataPost(_o)
    indicators['i'] = len(_o.history)
    _o.addToHistory({'time': timeObj, 'parsed': data})
    _o.indicators.append(indicators)
    return jsonify(indicators) # return jsonify(res)

###############################################################################################################

if __name__ == '__main__':
    _o = Context()
    PORT = 5008
    threading_func_wrapper(lambda: run_simple('localhost', PORT, app))
    print(f"http://localhost:{PORT}/api/hose-indicators-outound")
    print(f"http://localhost:{PORT}/shutdown ")