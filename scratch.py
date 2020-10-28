from common import *
from parser import *


def appendFile(data, fn=None):
    import json
    from CONSTANT import OUTPUT_TEXT_FILENAME
    if fn is None: fn = OUTPUT_TEXT_FILENAME
    with open(fn,"a+") as file:
        file.write(json.dumps(data) + "\n")
    return

data = loadData()
i= 0
#%%

list(data[-1].keys())
data[-1]['time']['time']

#%%
def loadInterval():
    with open("CONSTANT.py", "r") as file:
        lines = file.readlines()
    for line in lines:
        if line.__contains__("SAVE_INTERVAL"):
            return int(line.split("=")[1].strip())
