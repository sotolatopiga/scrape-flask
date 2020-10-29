from Test import loadData_2020_10_28
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
from utilities import *
# from receiveData import *
from common import mmap, dump, threading_func_wrapper
from Context import Context
from werkzeug.wrappers import Request, Response
import json, pickle

from requestHandler import handleHoseDataPost


app = Flask(__name__)
CORS(app)

#############################################################################################################

@app.route('/api/phaisinh-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def psListener():
    from flask import request
    return


@app.route('/')
def index():
    a = {'name': 'Sarah', 'age': 34, 'isEmployed': True}
    return json.dumps(a)


@app.route('/api/hose-indicators-outound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hose_indicators_outound():
    o.maybeUpdatedicators()
    return jsonify(o.indicators)


@app.route('/api/hose-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hose_snapshot_inbound():
    from flask import request
    timeObj, timeStr, data, indicators = handleHoseDataPost(request)
    indicators['i'] = len(o.history)
    o.addToHistory({'time': timeObj, 'parsed': data})
    o.indicators.append(indicators)
    print(f"\r#### {len(o.history)} ####", end="")
    return jsonify(indicators) # return jsonify(res)


@app.route("/shutdown")
def shutdown():
    shutdown_server()
    return "Successfully closed server"


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


o = Context()
