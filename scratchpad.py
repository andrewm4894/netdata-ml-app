#%%

from apps.config.config import get_config

app_config = get_config()
print(app_config)


#%%

from netdata_pandas.data import get_data

df = get_data(freq='10s')

#%%