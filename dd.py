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

with open("HOSE-stream.pickle", "wb") as file:
    pickle.dump({"start": data[0], "steps":lst}, file)

# Measure the number of stocks that have their prices changed
list(map(lambda diff: len(set(map(lambda x: x[1][0], diff))), lst))
