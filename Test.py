from utilities import *
import pickle

def loadData_2020_10_28():
    import pickle
    fn = "data/data.pickle-14_48_13(150).pickle"
    with open(fn, "rb") as file:
        data = pickle.load(file)
    return data

def loadSample():
    with open("sample.pickle", "rb") as file: return pickle.load(file)

def writeSample(x):
    with open("sample.pickle", "wb") as file: pickle.dump(x[1000:1500], file)# data = loadData_2020_10_28()
######################################################################################################

# with open("data/data.pickle-11_33_19(150).pickle", "rb") as file: x = pickle. load(file)

# x=loadSample; indicators = getIndicators(x)