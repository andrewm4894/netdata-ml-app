#%%

#%%

from netdata_pandas.data import get_data
from apps.changepoint.core import get_changepoints
from am4894plots.plots import plot_lines, plot_lines_grid
import time
import stumpy
import numpy as np

#%%

# inputs
hosts = ['34.75.17.189:19999']
charts_regex = '.*'
#charts_regex = 'system.*'
#charts_regex = '^(?!.*uptime).*$'
before = 0
after = -60*60*4
smooth_n = 10

#%%

# get the data
df = get_data(hosts=hosts, charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
df = df[[col for col in df.columns if 'uptime' not in col]]
print(df.shape)
df = df.rolling(smooth_n).mean()
#df.head()

#%%

#m = np.random.choice([60, 120, 360])
m = 30
dim = np.random.choice(df.columns)
df_tmp = df[[dim]].dropna()
mp = stumpy.stump(df_tmp[dim], m=m, ignore_trivial=True)
mp_dists = mp[:, 0]
n_fill = len(df_tmp) - len(mp_dists)
filler = np.empty(n_fill)
filler.fill(np.nan)
mp_dists = np.concatenate((filler, mp_dists.astype(float)))
df_tmp['mp'] = mp_dists

##%%

#df_norm = ((df_tmp-df_tmp.min())/(df_tmp.max()-df_tmp.min()))
#df_norm = df_norm.dropna(how='all', axis=1)
#df_norm = df_norm.dropna(how='all', axis=0)
df_norm = df_tmp
mp_std = round(df_norm['mp'].std(), 2)
mp_range = round(df_norm['mp'].max() - df_norm['mp'].min(), 2)

plot_lines_grid(df_norm, title=f"mp_std={mp_std}, mp_range={mp_range}",
           marker_list=[(pd.Timestamp(x), 'xx') for x in list(np.random.choice(df_norm.index.values.tolist(), 2))]
           )

#%%

#%%

#%%

xxx

#%%
import pandas as pd

print([(pd.Timestamp(x), 'xx') for x in list(np.random.choice(df_norm.index.values.tolist(), 2))])

#%%

#%%

import plotly.graph_objects as go

fig = go.Figure(
    data=go.Scatter(
        x=df_tmp.index, y=df_tmp[dim]
    )
)
fig.show()

#%%

#%matplotlib inline

import pandas as pd
import stumpy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.patches import Rectangle
import datetime as dt

plt.rcParams["figure.figsize"] = [20, 6]  # width, height
plt.rcParams['xtick.direction'] = 'out'

##%%

np.argwhere(mp[:, 0] == mp[:, 0].max()).flatten()[0]
#mp

##%%


fig, axs = plt.subplots(2, sharex=True, gridspec_kw={'hspace': 0})
plt.suptitle('Discord (Anomaly/Novelty) Discovery', fontsize='30')

axs[0].plot(df[dim].values)
axs[0].set_ylabel(dim, fontsize='20')
#rect = Rectangle((np.argwhere(mp[:, 0] == mp[:, 0].max()).flatten()[0], 0), m, 40, facecolor='lightgrey')
#axs[0].add_patch(rect)
axs[1].set_xlabel('Time', fontsize ='20')
axs[1].set_ylabel('Matrix Profile', fontsize='20')
axs[1].axvline(x=np.argwhere(mp[:, 0] == mp[:, 0].max()).flatten()[0], linestyle="dashed")
axs[1].plot(mp[:, 0])
plt.show()

#%%

xxx

#%%

plt.suptitle('Steamgen Dataset', fontsize='30')
plt.xlabel('Time', fontsize ='20')
plt.ylabel('Steam Flow', fontsize='20')
plt.plot(steam_df['steam flow'].values)
plt.show()

#%%

m = int(640)
mp = stumpy.stump(steam_df['steam flow'], m)

#%%

fig, axs = plt.subplots(2, sharex=True, gridspec_kw={'hspace': 0})
plt.suptitle('Motif (Pattern) Discovery', fontsize='30')

axs[0].plot(steam_df['steam flow'].values)
axs[0].set_ylabel('Steam Flow', fontsize='20')
rect = Rectangle((643, 0), m, 40, facecolor='lightgrey')
axs[0].add_patch(rect)
rect = Rectangle((8724, 0), m, 40, facecolor='lightgrey')
axs[0].add_patch(rect)
axs[1].set_xlabel('Time', fontsize ='20')
axs[1].set_ylabel('Matrix Profile', fontsize='20')
axs[1].axvline(x=643, linestyle="dashed")
axs[1].axvline(x=8724, linestyle="dashed")
axs[1].plot(mp[:, 0])
plt.show()

#%%

fig, axs = plt.subplots(2, sharex=True, gridspec_kw={'hspace': 0})
plt.suptitle('Discord (Anomaly/Novelty) Discovery', fontsize='30')

axs[0].plot(steam_df['steam flow'].values)
axs[0].set_ylabel('Steam Flow', fontsize='20')
rect = Rectangle((3864, 0), m, 40, facecolor='lightgrey')
axs[0].add_patch(rect)
axs[1].set_xlabel('Time', fontsize ='20')
axs[1].set_ylabel('Matrix Profile', fontsize='20')
axs[1].axvline(x=3864, linestyle="dashed")
axs[1].plot(mp[:, 0])
plt.show()

#%%

#%%