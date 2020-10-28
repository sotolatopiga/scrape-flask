from flask import Flask
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import numpy as np
# from receiveData import *
import json
from parser import parseHose, compute
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



# https://stackoverflow.com/questions/14248296/making-http-requests-using-chrome-developer-tools
# https://riptutorial.com/flask/example/5832/receiving-json-from-an-http-request

history =[]
@app.route('/api/echo-json', methods=['GET', 'POST', 'DELETE', 'PUT'])
def add():
    from common import dump
    data = request.get_json()
    time = data['time']
    data = data['data']
    data = parseHose(data)
    timestr = time['time'].replace("_", ":", )
    indicators = compute(data)
    history.append({'time': time, 'parsed': data})
    dump(history)
    print(f"\r#### {len(history)} ####", np.array(list(indicators.values()))/1000000000, end= "")
    res = f"#### {len(history)} #### successfully received data @ {timestr}, with {len(data)} stock symbols. Summary: {indicators}"

    return jsonify(res)

"""
Posting data to Flask Server and parsing, then using the result that Server sent back
fetch('http://127.0.0.1:5000/api/echo-json', {
  method: 'POST',
  body: JSON.stringify({
    title: 'foo',
    body: 'bar',
    userId: 1
  }),
  headers: {
    'Content-type': 'application/json; charset=UTF-8'
  }
})
.then(res => res.json())
.then(console.log)
"""


"""
Requesting data from the host
fetch('http://localhost:5000')
  .then(res => res.json())
  .then(console.log)
"""