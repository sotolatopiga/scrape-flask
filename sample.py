import pandas as pd
index = pd.date_range('1/1/2000', periods=9, freq='D')


#%%
import pandas as pd, numpy as np
index = pd.to_datetime(np.array(range(1349720105, 1349723705)), unit = 's')
df = pd.Series(range(len(index)), index = index)
from pandas import DatetimeIndex
import pandas as pd, numpy as np

# 1349720105