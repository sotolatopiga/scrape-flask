from flask import request, jsonify
from utilities import parseHose, computeIndicators

_lastPsData = ""


def toHour(data):
    time = data['time']
    return (time['hour'] * 3600 + time['minute'] * 60 + time['second']) / 3600


def handleHoseDataPost(o):
    raw = request.get_json()
    time = raw['time']
    data = raw['data']
    data = parseHose(data)
    timestr = time['time'].replace("_", ":", )
    indicators = computeIndicators(data, time); indicators['hour'] = toHour(raw)
    print(f"\r#### {len(o.history)} ####", end="")
    return time, timestr, data, indicators


def handlePsDataPost(o):
    global _lastPsData
    data = request.get_json()
    noUpdate = data['data'] == _lastPsData
    orders = list(reversed(data['orders']))
    o.maybeUpdateOrders(orders)
    if not noUpdate:
        _lastPsData = data['data']
        o.psHistory.append(data['data'])
    hour = toHour(data)
    return {'psHistory': len(o.psHistory),
            'psOrder' : len(o.psOrders),
            'msg': "from /api/ps-snapshot-inbound",  }


def handlePsDataGet(o):
    return jsonify({'msg': "from /api/ps-ohlc-outbound", 'data': o.psOrders})

def handleHoseDataGet(o):
    o.maybeUpdatedicators()
    return jsonify({'data': o.indicators, 'msg': "from /api/hose-indicators-outbound"})


#################################################################################################################

# https://stackoverflow.com/questions/14248296/making-http-requests-using-chrome-developer-tools
# https://riptutorial.com/flask/example/5832/receiving-json-from-an-http-request


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

function myFoo() {
    fetch('http://localhost:5003/api/hose-indicators-outound')
  .then(res => res.json())
  .then(res => console.log(res))}

myRequestInterval = setInterval(myFoo, 3000); myFoo();
"""