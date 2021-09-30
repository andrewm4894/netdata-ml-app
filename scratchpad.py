# used for playing with random dev code

#%%

import requests
import pandas as pd
from apps.core.utils.inputs import parse_netdata_url
from netdata_pandas.data import get_data
import matplotlib.pyplot as plt

netdata_url = 'http://34.73.38.236:19999/#menu_anomaly_detection_submenu_anomaly_detection;after=1632948226000;before=1632950039000;theme=slate;utc=Europe/Dublin'
anomaly_event_start_buffer = 5
anomaly_event_end_buffer = 1
top_n = 5

url_dict = parse_netdata_url(netdata_url)
host = url_dict['host:port']
after = url_dict['fragments']['after']
before = url_dict['fragments']['before']

url_anomaly_events = f"http://{host}/api/v1/anomaly_events?after={after}&before={before}"
anomaly_events = requests.get(url_anomaly_events).json()
df_anomaly_events = pd.DataFrame()

for anomaly_event in anomaly_events:
    anomaly_event_start = anomaly_event[0]
    anomaly_event_end = anomaly_event[1]
    anomaly_event_len = anomaly_event_end - anomaly_event_start
    url_anomaly_event = f"http://{url_dict['host:port']}/api/v1/anomaly_event_info?after={anomaly_event_start}&before={anomaly_event_end}"
    anomaly_event = requests.get(url_anomaly_event).json()
    df_anomaly_event = pd.DataFrame(anomaly_event, columns=['anomaly_rate', 'chart|dim'])
    df_anomaly_event['anomaly_event_start'] = anomaly_event_start
    df_anomaly_event['anomaly_event_end'] = anomaly_event_end
    df_anomaly_event['chart'] = df_anomaly_event['chart|dim'].str.split('|').str[0]
    df_anomaly_event['dim'] = df_anomaly_event['chart|dim'].str.split('|').str[1]
    df_anomaly_event = df_anomaly_event[['anomaly_event_start', 'anomaly_event_end', 'chart|dim', 'chart', 'dim', 'anomaly_rate']]

    charts = df_anomaly_event['chart'].unique().tolist()
    after = anomaly_event_start - (anomaly_event_len * anomaly_event_start_buffer)
    before = anomaly_event_end + (anomaly_event_len * anomaly_event_end_buffer)

    df_anomaly_event_raw = get_data(hosts=host, charts=charts, after=after, before=before)
    df_anomaly_event_raw = df_anomaly_event_raw[df_anomaly_event['chart|dim']]

    df_anomaly_event_bit = get_data(hosts=host, charts=charts, after=after, before=before, options='anomaly-bit')
    df_anomaly_event_bit = df_anomaly_event_bit[df_anomaly_event['chart|dim']]
    df_anomaly_event_bit = df_anomaly_event_bit.add_suffix('_bit')

    df_anomaly_event_data = df_anomaly_event_raw.join(df_anomaly_event_bit)
    for chart_dim, anomaly_rate in df_anomaly_event[['chart|dim', 'anomaly_rate']].head(top_n).values.tolist():
        chart_title = f'{chart_dim} (ar={round(anomaly_rate,2)})'
        ax = df_anomaly_event_data[[chart_dim]].plot(title=chart_title, figsize=(14, 10))
        df_anomaly_event_data[[f'{chart_dim}_bit']].plot(secondary_y=True, ax=ax)
        plt.show()


#%%



#%%