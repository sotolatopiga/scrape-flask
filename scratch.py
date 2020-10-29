from common import *


def appendFile(data, fn=None):
    import json
    from CONSTANT import OUTPUT_TEXT_FILENAME
    if fn is None: fn = OUTPUT_TEXT_FILENAME
    with open(fn,"a+") as file:
        file.write(json.dumps(data) + "\n")
    return

def loadInterval():
    with open("CONSTANT.py", "r") as file:
        lines = file.readlines()
    for line in lines:
        if line.__contains__("SAVE_INTERVAL"):
            return int(line.split("=")[1].strip())


def loadData_2020_10_28():
    import pickle
    fn = "data/data.pickle-14_48_13(150).pickle"
    with open(fn, "rb") as file:
        data = pickle.load(file)
    return data






