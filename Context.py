from common import mmap, dump, threading_func_wrapper
from forFrontend import computeIndicatorsFromSnapShot
import json

class Context:

    def __init__(self, indicatorFunc= computeIndicatorsFromSnapShot):
        self.history = []
        self.indicators = []
        self.psHistory = []
        self.psOrders = []
        self.indicatorsFunc = indicatorFunc


    def maybeUpdateOrders(self, orders):
        if len(orders) > len(self.psOrders):
            self.psOrders = orders
            return True
        else: return False


    def maybeUpdatedicators(self):
        def foo(i):
            return computeIndicatorsFromSnapShot(self.history[i]['parsed'], self.history[i]['time'])
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


o = Context()