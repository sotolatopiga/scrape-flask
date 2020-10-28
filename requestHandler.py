def handleHoseDataPost(req):
    from flask import request
    from parser import parseHose, computeIndicators
    data = request.get_json()
    timeObj = data['time']
    time = data['time']
    data = data['data']
    data = parseHose(data)
    timestr = time['time'].replace("_", ":", )
    indicators = computeIndicators(data)
    return timeObj, timestr, data, indicators

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
fetch('http://localhost:5000')
  .then(res => res.json())
  .then(console.log)
"""