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


def loadData_2020_10_28():
    import pickle
    fn = "data/data.pickle-14_48_13(150).pickle"
    with open(fn, "rb") as file:
        data = pickle.load(file)
    return data

data = loadData_2020_10_28()
#%%
import dictdiffer
import sys
from copy import copy
diff = list(dictdiffer.diff(data[0], copy(data[1])))
import pickle
with open("test.pickle", "wb") as file: pickle.dump(data[0], file)
#%%
lst = []
for i in range(1, len(data)):
    print(f"\rsnapshot #{i}/{len(data)}: calculating differences", end="")
    lst.append(list(dictdiffer.diff(data[i]['parsed'], data[i-1]['parsed'])))
#%%
with open("test.pickle", "wb") as file: pickle.dump({"start": data[0], "steps":lst}, file)

for i in range(1, len(data)-1):
    if len(lst[i]) == 0 : print(i)

# Measure the number of stocks that have their prices changed
list(map(lambda diff: len(set(map(lambda x: x[1][0], diff))), lst))

