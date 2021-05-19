#%%

#%%

from netdata_pandas.data import get_data

host = 'london.my-netdata.io'
df = get_data(hosts=[host], charts_regex='system.cpu')
print(df.shape)

#%%

import numpy as np
import pandas as pd

df = pd.DataFrame(
    data=np.where(df >= 1.00, 1, 0),
    columns=df.columns,
    index=df.index
)
#%%