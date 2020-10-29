from Test import loadData_2020_10_28
from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
from utilities import *
# from receiveData import *
from common import dump
import json, pickle
from requestHandler import handleHoseDataPost


app = Flask(__name__)
CORS(app)


class Context:

    def __init__(self):
        self.history = []
        self.indicators = []


    def maybeComputeIndicators(self):
        if len(self.indicators) < len(self.history):
            lst = []
            for i in range(len(self.indicators), len(self.history)):
                lst.append(self.history[i])
            indicatorsUpdate = getIndicators(lst)
            self.indicators += indicatorsUpdate
        assert len(self.indicators) == len(self.history)


    def getIndicators(self):
        print(self.history[-1].keys())
        # print("hisotry: ", self.history[-1])
        getIndicators([self.history[-1]])
        # self.maybeComputeIndicators()
        return self.indicators


    def addToHistory(self, data):
        self.history.append(data)


    def maybeDumpHistoryToDisk(self):
        dump(self.history)


o = Context()


@app.route('/api/phaisinh-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def psListener():
    from flask import request
    return


@app.route('/')
def index():
    a = {'name': 'Sarah', 'age': 34, 'isEmployed': True}
    return json.dumps(a)


@app.route('/api/hose-indicators-outound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hoseOutputIndicators():
    return jsonify({"msg": "cool"})


@app.route('/api/hose-snapshot-inbound', methods=['GET', 'POST', 'DELETE', 'PUT'])
def hoseSnapshotListener():
    from flask import request
    timeObj, timeStr, data, indicators = handleHoseDataPost(request)
    o.addToHistory({'time': timeObj, 'parsed': data})
    o.maybeDumpHistoryToDisk()
    o.getIndicators()
    print(f"\r#### {len(o.history)} ####",  end= "")
    res = f"#### {len(o.history)} #### successfully received data @ {timeStr}, " \
          f"with {len(data)} stock symbols. Summary: {indicators}"
    return jsonify(res)

# data = loadData_2020_10_28()
#%%
######################################################################################################
#with open("sample.pickle", "wb") as file: pickle.dump(x[1000:1500], file)



# with open("sample.pickle", "rb") as file: x = pickle. load(file)
# indicators = getIndicators(x);print(indicators[200:300])

