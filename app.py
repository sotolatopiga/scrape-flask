from flask import Flask
from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
# from receiveData import *
import json
from requestHandler import handleHoseDataPost
from parser import parseHose, computeIndicators
import pickle


app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    a = {'name': 'Sarah', 'age': 34, 'isEmployed': True}
    return json.dumps(a)



@app.route('/user/<name>')
def user(name):
    print(name)
    a = {'name': name, 'age': 14, 'isEmployed': True}
    return json.dumps(a)



history =[]
@app.route('/api/echo-json', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hoseListener():
    from common import dump
    from flask import request
    timeObj, timeStr, data, indicators = handleHoseDataPost(request)
    history.append({'time': timeObj, 'parsed': data})
    dump(history)
    print(f"\r#### {len(history)} ####", np.array(list(indicators.values()))/1000000000, end= "")
    res = f"#### {len(history)} #### successfully received data @ {timeStr}, " \
          f"with {len(data)} stock symbols. Summary: {indicators}"
    return jsonify(res)
