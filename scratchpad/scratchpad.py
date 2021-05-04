#%%

#%%

from netdata_pandas.data import get_data

host = 'london.my-netdata.io'
after = 1620132660
before = 1620133560
df = get_data(hosts=[host], charts_regex='system.cpu', after=after, before=before, index_as_datetime=True, protocol='https')
print(df.shape)

#%%