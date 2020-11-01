from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__': # run this with python exposed.py
    app.run(host='0.0.0.0', debug = False)


# https://flask.palletsprojects.com/en/1.1.x/quickstart/