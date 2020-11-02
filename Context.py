from common import mmap, dump, threading_func_wrapper
from DB_CONSTANTS import db as DB, COL_O_HISTORY, COL_O_INDICATORS, COL_O_PS_ORDERS, COL_HOSE_RAW, TEMP_PICKLE
from copy import deepcopy
import json
import pickle

class Context:

    def __init__(self):
        self.history = []
        self.indicators = []
        self.psHistory = []


    def maybeUpdateOrders(self, orders):
        if len(orders) > len(self.psHistory):
            self.psHistory = orders
            return True
        else: return False


    def maybeUpdatedicators(self):
        def foo(i):
            return None
        if len(self.indicators) < len(self.history):
            update = mmap(foo, range(len(self.indicators), len(self.history)))
            self.indicators += update
        assert len(self.indicators) == len(self.history)


    def getIndicators(self):
        self.maybeUpdatedicators()
        return self.indicators


    def addToHistory(self, data):
        self.history.append(data)
        self.maybeDumpHistoryToDisk()


    def maybeDumpHistoryToDisk(self):
        dump(self.history)


    def chache(self):
        with open("serverContext.json", "w") as file:
            json.dump({"lastHistory": self.history[-1],
                       "psHistory": self.psHistory, "psOrder": self.psOrders}, file)

    def saveToDB(self, db=DB):
        try:
            db[COL_HOSE_RAW].drop()
            db[COL_O_HISTORY].drop()
            db[COL_O_PS_ORDERS].drop()
            db[COL_O_INDICATORS].drop()
        finally:

            with open(TEMP_PICKLE, 'wb') as file:
                pickle.dump([self.indicators, self.psHistory], file)
            with open(TEMP_PICKLE, 'rb') as file:
                indicators, psHistory = pickle.load(file)
            db[COL_O_PS_ORDERS].insert_many(deepcopy(self.psHistory))
            db[COL_O_PS_ORDERS].insert_many(indicators)



    def saveIndicatorToDB(self, db=DB):
        try:
            db[COL_O_PS_ORDERS].drop()
            db[COL_O_INDICATORS].drop()
        finally:
            db[COL_O_PS_ORDERS].insert_many(self.psHistory)
            db[COL_O_INDICATORS].insert_many(deepcopy(self.indicators))


    def probeDB(self, db=DB):
        print(len(list(db[COL_O_INDICATORS].find())))

_o = Context()