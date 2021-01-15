#%%

from netdata_pandas.data import get_data
from apps.changepoint.core import get_changepoints
from am4894plots.plots import plot_lines

##%%

# inputs
hosts = ['london.my-netdata.io']
#charts_regex = '.*'
#charts_regex = '.*'
charts_regex = '^(?!.*uptime).*$'
before = 0
after = -60*15
smooth_n = 5
n_samples = 50
sample_len = 50

##%%

# get the data
df = get_data(hosts=hosts, charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
#df = df[[col for col in df.columns if 'uptime' not in col]]
print(df.shape)
df.head()

##%%

# add some smoothing
df = df.rolling(smooth_n).mean()

##%%

df_norm = ((df-df.min())/(df.max()-df.min()))
df_norm = df_norm.dropna(how='all', axis=1)
df_norm = df_norm.dropna(how='all', axis=0)

##%%

# get changepoints
df_results = get_changepoints(df_norm, n_samples, sample_len)

#%%

#%%

#%%

#%%

for i, row in df_results.head(20).iterrows():

    metric = row['metric']
    quality_score = row['quality_score']
    quality_rank = row['quality_rank']
    changepoint = row['changepoint']
    abs_mean_pct_diff = row['abs_mean_pct_diff']
    title = f'{metric} - rank={quality_rank}, qs={quality_score}, abs_mean_pct_diff={abs_mean_pct_diff}'
    if quality_score <= 0.1 and abs_mean_pct_diff >= 0.3:
        plot_lines(df, [metric], title=title, shade_regions=[(changepoint, df.index.max(), 'grey')])

#%%

#%%

#%%

#%%

#%%


