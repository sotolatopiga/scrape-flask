
def loadData_2020_10_28():
    import pickle
    fn = "data/data.pickle-14_48_13(150).pickle"
    with open(fn, "rb") as file:
        data = pickle.load(file)
    return data
