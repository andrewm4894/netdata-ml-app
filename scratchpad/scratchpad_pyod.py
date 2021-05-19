#%%

#%%

from netdata_pandas.data import get_data
from am4894plots.plots import plot_lines, plot_lines_grid, plot_heatmap
import time
from pyod.models.hbos import HBOS
from pyod.models.pca import PCA
import numpy as np
import pandas as pd
from datetime import timedelta

def make_features_np(arr, lags_n, diffs_n, smooth_n, colnames):
    def lag(arr, n):
        res = np.empty_like(arr)
        res[:n] = np.nan
        res[n:] = arr[:-n]
        return res

    if diffs_n > 0:
        arr = np.diff(arr, diffs_n, axis=0)
        arr = arr[~np.isnan(arr).any(axis=1)]

    if smooth_n > 1:
        arr = np.cumsum(arr, axis=0, dtype=float)
        arr[smooth_n:] = arr[smooth_n:] - arr[:-smooth_n]
        arr = arr[smooth_n - 1:] / smooth_n

    if lags_n > 0:
        colnames = colnames + [f'{col}_lag{lag}' for lag in range(1, lags_n + 1) for col in colnames]
        arr_orig = np.copy(arr)
        for lag_n in range(1, lags_n + 1):
            arr = np.concatenate((arr, lag(arr_orig, lag_n)), axis=1)
        arr = arr[~np.isnan(arr).any(axis=1)]

    return colnames, arr

##%%

# inputs
hosts = ['london.my-netdata.io']
#charts_regex = '.*'
charts_regex = 'system.*'
#charts_regex = '^(?!.*uptime).*$'
before = 0
after = -60*60*1
smooth_n = 3
diffs_n = 1
lags_n = 3

##%%

# get the data
df = get_data(hosts=hosts, charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
df = df[[col for col in df.columns if 'uptime' not in col]]
print(df.shape)
#df.head()

##%%

ref_timedelta = timedelta(hours=4)

# work out reference window
ref_before = int(df.index.min().timestamp())
ref_after = int((df.index.min() - ref_timedelta).timestamp())

# get the reference data
df_ref = get_data(hosts=hosts, charts_regex=charts_regex, after=ref_after, before=ref_before,
                  index_as_datetime=True)
print(df_ref.shape)

##%%

arr = df.values
colnames = list(df.columns)
colnames, arr = make_features_np(arr, lags_n, diffs_n, smooth_n, colnames)
df_features = pd.DataFrame(arr, columns=colnames).ffill().bfill()

arr_ref = df_ref.values
colnames_ref = list(df_ref.columns)
colnames_ref, arr_ref = make_features_np(arr_ref, lags_n, diffs_n, smooth_n, colnames_ref)
df_features_ref = pd.DataFrame(arr_ref, columns=colnames_ref).ffill().bfill()

##%%

charts = list(set([col.split('|')[0] for col in df.columns]))
preds = {}
probs = {}

for chart in charts:
    chart_cols = [col for col in df_features.columns if col.startswith(f'{chart}|')]
    model = PCA(contamination=0.01)
    X_ref = df_features_ref[chart_cols].values
    X = df_features[chart_cols].values
    try:
        model.fit(X_ref)
        preds[chart] = model.predict(X)
        probs[chart] = model.predict_proba(X)[:, 1].tolist()
    except:
        print(f'{chart} defaulting to HBOS')
        model = HBOS(contamination=0.01)
        model.fit(X_ref)
        preds[chart] = model.predict(X)
        probs[chart] = model.predict_proba(X)[:, 1].tolist()


df_preds = pd.DataFrame.from_dict(preds, orient='columns')
df_probs = pd.DataFrame.from_dict(probs, orient='columns')

##%%

df_preds['time'] = df.tail(len(df_preds)).index
df_preds = df_preds.set_index('time')
df_probs['time'] = df.tail(len(df_probs)).index
df_probs = df_probs.set_index('time')

##%%

plot_lines_grid(df_probs, h=1200, yaxes_visible=False, xaxes_visible=False, subplot_titles=['' for i in range(len(df_probs.columns))])
plot_lines_grid(df_preds, h=1200, yaxes_visible=False, xaxes_visible=False, subplot_titles=['' for i in range(len(df_preds.columns))])
#plot_heatmap(df_preds)
#plot_heatmap(df_probs)

#%%

list(df_preds.sum().sort_values(ascending=False).index)

#%%

#%%

xxx

#df_preds.mean()
#df_probs.mean()

#%%


#df_norm = ((df-df.min())/(df.max()-df.min()))
#df_norm = df_norm.dropna(how='all', axis=1)
#df_norm = df_norm.dropna(how='all', axis=0)

#%%

chart = 'system.cpu'
cols = [col for col in df.columns if col.startswith(f'{chart}|')]
df_tmp = df_norm[cols].tail(len(df_probs))
df_tmp['anomaly_score'] = df_probs[chart].values
df_tmp['anomalies'] = df_preds[chart].values
shade_regions = [(i, i + timedelta(seconds=5), 'red') for i in df_tmp[df_tmp['anomalies'] == 1].index]
plot_lines(df_tmp, cols, shade_regions=shade_regions)


#%%



#%%

#%%

df_probs[chart]

#df_preds.rolling(15).mean().mean()

#%%

#%%

#model.predict_proba(X)[:, 1].tolist()

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