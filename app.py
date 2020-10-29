from Test import loadData_2020_10_28
from flask import Flask, jsonify, request
from flask_cors import CORS
from common import mmap, dump, threading_func_wrapper
from Context import Context
import json, pickle
from requestHandler import handleHoseDataPost, handlePsDataPost

app = Flask(__name__)
CORS(app)

#############################################################################################################

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


@app.route('/api/phaisinh-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def psListener():
    from flask import request
    return


# Home page
@app.route('/')
def index():
    a = {'name': 'Sarah', 'age': 34, 'isEmployed': True}
    return json.dumps(a)


# Return hose indicators for charts
@app.route('/api/hose-indicators-outound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hose_indicators_outbound():
    o.maybeUpdatedicators()
    return jsonify(o.indicators)


# Ingest phai sinh data
@app.route('/api/ps-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def ps_snapshot_inbound():
    noUpdate, hour, data =handlePsDataPost(o)
    return jsonify({'psHistory': len(o.psHistory)})


# Ingest HOSE data
@app.route('/api/hose-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hose_snapshot_inbound():
    timeObj, timeStr, data, indicators = handleHoseDataPost(o)
    indicators['i'] = len(o.history)
    o.addToHistory({'time': timeObj, 'parsed': data})
    o.indicators.append(indicators)
    return jsonify(indicators) # return jsonify(res)


if __name__ == '__main__':
    o = Context()
    PORT = 5003
    from werkzeug.serving import run_simple
    threading_func_wrapper(lambda: run_simple('localhost', PORT, app))
    print(f"http://localhost:{PORT}/api/hose-indicators-outound")
    print(f"http://localhost:{PORT}/shutdown ")