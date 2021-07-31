# used for playing with random dev code

#%%

import pandas as pd
import numpy as np
from netdata_pandas.data import get_data
from scipy.spatial.distance import cdist
from am4894plots.plots import plot_lines_grid

host = 'london.my-netdata.io'
after = -60
before = 0
metric = 'system.cpu|user'
top_n = 20

df = get_data(hosts=[host], after=after, before=before, charts=['all'])
df = (df-df.min())/(df.max()-df.min())
df = df.fillna(0)
print(df.shape)

df_dist = pd.DataFrame(
    data=zip(df.columns, cdist(df[[metric]].fillna(0).transpose(), df.fillna(0).transpose(), 'cosine')[0]),
    columns=['metric', 'distance']
)
df_dist['similarity'] = 1 - df_dist['distance']
df_dist['rank'] = df_dist['similarity'].rank(ascending=False)
df_dist = df_dist.sort_values('rank')

plot_cols = df_dist.head(top_n)['metric'].values.tolist()
plot_lines_grid(
    df,
    plot_cols,
    h_each=200, legend=False, yaxes_visible=False, xaxes_visible=False,
    subplot_titles=[f'{x[0]} ({round(x[1],2)})' for x in df_dist.head(top_n)[['metric', 'similarity']].values.tolist()]
)


#%%

#%%