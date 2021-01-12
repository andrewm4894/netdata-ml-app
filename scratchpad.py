#%%

from datetime import datetime, timedelta
import time
from netdata_pandas.data import get_data
import pandas as pd
import matplotlib.pyplot as plt
import ruptures as rpt
import numpy as np
from numpy import dot
from numpy.linalg import norm
from scipy.stats import ks_2samp
from am4894plots.plots import plot_lines

##%%

# inputs
hosts = ['london.my-netdata.io']
charts_regex = 'system.*'
before = 0
after = -60*15
smooth_n = 10
n_samples = 10
sample_len = 30

##%%

# get the data
df = get_data(hosts=hosts, charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
print(df.shape)
df.head()

##%%

# add some smoothing
df = df.rolling(smooth_n).mean()

# list to save results in
results = []

for col in df.columns:

    x = df[col].dropna().values
    algo = rpt.Window(width=100, model='l2').fit(x)
    breakpoints = algo.predict(n_bkps=1)
    num_breakpoints = len(breakpoints)

    # if breakpoint found
    if num_breakpoints > 1:

        changepoint = breakpoints[0]
        changepoint_t = df.index[changepoint]
        x_post_breakpoints = x[breakpoints[0]:breakpoints[1]]
        x_pre_breakpoints = x[0:breakpoints[0]]
        breakpoints_len = len(x_post_breakpoints)
        metrics = []

        # run some samples
        for _ in range(n_samples):

            sample_start_pre = np.random.choice(range(len(x_pre_breakpoints) - sample_len))
            x_sample_pre = x_pre_breakpoints[sample_start_pre:sample_start_pre + sample_len]

            sample_start_post = np.random.choice(range(len(x_post_breakpoints) - sample_len))
            x_sample_post = x_post_breakpoints[sample_start_post:sample_start_post + sample_len]

            _, p = ks_2samp(x_sample_post, x_sample_pre)

            metrics.append(round(p, 4))

        quality_score = round(np.mean(metrics), 4)

        results.append([col, quality_score, changepoint_t])

##%%

df_results = pd.DataFrame(results, columns=['metric', 'quality_score', 'changepoint'])
df_results['quality_rank'] = df_results['quality_score'].rank(ascending=True, method='first')
df_results = df_results.sort_values('quality_rank', ascending=True)
df_results = df_results.reset_index()
print(df_results.shape)
print(df_results.head(10))

##%%

for i, row in df_results.iterrows():

    metric = row['metric']
    quality_score = row['quality_score']
    quality_rank = row['quality_rank']
    changepoint = row['changepoint']
    title = f'{metric} - rank={quality_rank}, qs={quality_score}'
    if quality_score <= 0.1:
        plot_lines(df, [metric], title=title, shade_regions=[(changepoint, df.index.max(), 'grey')])

#%%

#%%

#%%

#%%

#%%


