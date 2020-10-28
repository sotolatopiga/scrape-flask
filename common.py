BILLION = 1000 * 1000 * 1000
from CONSTANT import SAVE_INTERVAL

class C:
    COL_GIA3 = 3
    COL_VOL3 = 4
    COL_GIA2 = 5
    COL_VOL2 = 6
    COL_GIA1 = 7
    COL_VOL1 = 8

    COL_GIA = 9
    COL_VOL = 10

    COL_GIA1b = 12
    COL_VOL1b = 13
    COL_GIA2b = 14
    COL_VOL2b = 15
    COL_GIA3b = 16
    COL_VOL3b = 17
    COL_TOTAL_VOL = 18
    COL_AVG_PRICE = 21
    COL_HIGH = 22
    COL_LOW = 23
    NN_BUY = 24
    NN_SELL = 25

    DATA_2_PLOT_RATIO = 100000

    CTIME = "times"
    CBUYP = "buyPressure"
    CSELLP = "sellPressure"
    CHOSE="hoseSnapShot"
    LOCAL="local"


def exec3(cmd): #
  #print(f"****\n running: {cmd} ****")
  import subprocess
  process = subprocess.Popen(cmd.split(" "),
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()
  # print (stdout.decode("utf-8"), stderr.decode("utf-8"))
  return stdout.decode("utf-8"), f"""error code: {stderr.decode("utf-8")}"""


def threading_func_wrapper(func, delay=0.5, args=None, start=True):
    import threading
    if args is None:
        func_thread = threading.Timer(delay, func)
    else:
        func_thread = threading.Timer(delay, func, (args,))
    if start: func_thread.start()
    return func_thread



def mmap(*args):
    return list(map(*args))


def dump(history):
    from CONSTANT import OUTPUT_PICKLE_FILENAME
    import pickle
    n= len(history)
    if n == 0: return
    SAVE_INTERVAL = loadInterval()
    if not n % SAVE_INTERVAL == 0: return
    lastWrite = history[-1]
    fn ='-'.join([OUTPUT_PICKLE_FILENAME, lastWrite['time']['time']])
    with open(f"{fn}({SAVE_INTERVAL}).pickle", "wb") as file:
        pickle.dump(history, file)


#
def loadData():
    from CONSTANT import OUTPUT_PICKLE_FILENAME
    import pickle
    with open(OUTPUT_PICKLE_FILENAME, "rb") as file:
        return pickle.load(file)

def loadInterval():
    with open("CONSTANT.py", "r") as file:
        lines = file.readlines()
    for line in lines:
        if line.__contains__("SAVE_INTERVAL"):
            return int(line.split("=")[1].strip())

# data = load()
#%%


