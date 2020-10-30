with open("data/data-30_10_2020-bothSessions.pickle", "rb") as file:
    import pickle
    data = pickle.load(file)

print(len(data))

#%%

import dictdiffer
OUTPUT = "HOSE-stream-30_10_2020"
lst = []
for i in range(1, len(data)):
    print(f"\rsnapshot #{i}/{len(data)}: calculating differences", end="")
    lst.append(list(dictdiffer.diff(data[i]['parsed'], data[i-1]['parsed'])))

with open(f"{OUTPUT}.pickle", "wb") as file:
    pickle.dump({"start": data[0], "steps":lst}, file)

#%%
trimmedHistory = list(map(lambda i: data[i], range(0, len(data), 100)))
print(len(trimmedHistory))
with open(f"{OUTPUT}-trimmed.pickle", "wb") as file:
    pickle.dump(trimmedHistory, file)