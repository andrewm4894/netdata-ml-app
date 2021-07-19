# used for playing with random dev code

#%%

from netdata_pandas.data import get_data

#df = get_data(hosts='34.73.38.236:19999', points=10, charts_regex='system.*', options='anomaly-bit')
df = get_data(hosts='34.73.38.236:19999', points=5, charts_regex='system.*')
print(df.shape)


#%%

url_dict


#%%

#%%