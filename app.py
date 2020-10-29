
from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
from utilities import *
# from receiveData import *
import json, pickle
from requestHandler import handleHoseDataPost


app = Flask(__name__)
CORS(app)


@app.route('/api/data', methods=['GET', 'POST', 'DELETE', 'PUT'])
def psListener():
    from flask import request
    return

def loadData_2020_10_28():
    import pickle
    fn = "data/data.pickle-14_48_13(150).pickle"
    with open(fn, "rb") as file:
        data = pickle.load(file)
    return data


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
@app.route('/api/hose-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hoseListener():
    from common import dump
    from flask import request
    timeObj, timeStr, data, indicators = handleHoseDataPost(request)
    history.append({'time': timeObj, 'parsed': data})
    dump(history)
    print(f"\r#### {len(history)} ####",  end= "")
    res = f"#### {len(history)} #### successfully received data @ {timeStr}, " \
          f"with {len(data)} stock symbols. Summary: {indicators}"
    return jsonify(res)

# data = loadData_2020_10_28()
#%%
######################################################################################################
#with open("sample.pickle", "wb") as file: pickle.dump(x[1000:1500], file)



# with open("sample.pickle", "rb") as file: x = pickle. load(file)
# indicators = getIndicators(x);print(indicators[200:300])

