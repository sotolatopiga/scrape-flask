BILLION = 1000 * 1000 * 1000
from CONSTANT import SAVE_INTERVAL

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


