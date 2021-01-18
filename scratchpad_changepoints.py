#%%

from netdata_pandas.data import get_data
from apps.changepoint.core import get_changepoints
from am4894plots.plots import plot_lines
import time

##%%

# inputs
hosts = ['london.my-netdata.io']
#charts_regex = '.*'
#charts_regex = 'system.*'
charts_regex = '^(?!.*uptime).*$'
before = 0
after = -60*15
smooth_n = 5

##%%

# get the data
df = get_data(hosts=hosts, charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
df = df[[col for col in df.columns if 'uptime' not in col]]
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
time_start = time.time()
df_results = get_changepoints(df_norm)
time_end = time.time()
time_taken = round(time_end - time_start, 2)
print(f'time_taken={time_taken}')

#%%

#%%

#%%

#%%

for i, row in df_results.sort_values('rank').head(50).iterrows():

    metric = row['metric']
    qs = row['qs']
    rank = row['rank']
    cp = row['cp']
    title = f'{metric} - rank={rank}, qs={qs}'
    plot_lines(df, [metric], title=title, shade_regions=[(cp, df.index.max(), 'grey')])

#%%

#%%

#%%