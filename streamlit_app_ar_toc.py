
import requests
import streamlit as st
from collections import OrderedDict
from urllib.parse import urlparse
import re


def parse_netdata_url(url):
    if url.startswith('http'):
        url_parsed = urlparse(url)
        url_dict = {
            'host': url_parsed.hostname,
            'port': url_parsed.port,
            'host:port': f'{url_parsed.hostname}:{url_parsed.port}' if url_parsed.port else url_parsed.hostname,
            'fragments': {frag.split('=')[0]: frag.split('=')[1] for frag in url_parsed.fragment.split(';') if '=' in frag}
        }
    else:
        url_dict = {
            'fragments': {frag.split('=')[0]: frag.split('=')[1] for frag in url.split(';') if
                          '=' in frag}
        }

    if 'after' in url_dict['fragments']:
        url_dict['after_long'] = int(int(url_dict['fragments']['after']))
        url_dict['after'] = int(int(url_dict['fragments']['after']) / 1000)
    if 'before' in url_dict['fragments']:
        url_dict['before_long'] = int(int(url_dict['fragments']['before']))
        url_dict['before'] = int(int(url_dict['fragments']['before']) / 1000)

    if 'highlight_after' in url_dict['fragments']:
        url_dict['highlight_after_long'] = int(int(url_dict['fragments']['highlight_after']))
        url_dict['highlight_after'] = int(int(url_dict['fragments']['highlight_after']) / 1000)
    if 'highlight_before' in url_dict['fragments']:
        url_dict['highlight_before_long'] = int(int(url_dict['fragments']['highlight_before']))
        url_dict['highlight_before'] = int(int(url_dict['fragments']['highlight_before']) / 1000)

    child_host = re.search('/host/(.*?)/', url)
    child_host = child_host.group(1) if child_host else None
    print(child_host)
    if child_host:
        url_dict['child_host'] = child_host
        url_dict['host:port'] = url_dict['host:port'] + f'/host/{child_host}'

    return url_dict


netdata_url = st.text_input('netdata_agent_dashboard_url', value='http://london.my-netdata.io/#after=-900000;before=0;=undefined;theme=slate;utc=Europe%2FLondon')


url_dict = parse_netdata_url(netdata_url)
host = url_dict['host:port']
after = int(url_dict['fragments'].get('after', '-900000'))//1000
before = int(url_dict['fragments'].get('before', '0'))//1000
highlight_after = int(url_dict['fragments'].get('highlight_after', '0'))//1000
highlight_before = int(url_dict['fragments'].get('highlight_before', '0'))//1000

after = highlight_after if highlight_after > 0 else after
before = highlight_before if highlight_before > 0 else before

print(highlight_after)
print(highlight_before)
print(after)
print(before)

url_weights = f"http://{host}/api/v1/weights?after={after}&before={before}&options=raw"
print(url_weights)

url_charts = f"http://{host}/api/v1/charts"
charts_data = requests.get(url_charts).json()['charts']
data_chart_order = dict()
for chart in charts_data:
    data_chart_order[chart] = dict()
    data_chart_order[chart]['priority'] = charts_data[chart]['priority']
    data_chart_order[chart]['context'] = charts_data[chart]['context']
print(data_chart_order)

#%%

import pandas as pd

df_chart_order = pd.DataFrame.from_dict(data_chart_order).transpose().reset_index()
df_chart_order.columns = ['chart', 'priority', 'context']
df_chart_order = df_chart_order[['context', 'chart', 'priority']].sort_values('priority')
df_chart_order['menu'] = df_chart_order['context'].str.split('.').str[0]

#%%

weights_data = requests.get(url_weights).json()

#%%

df_menu_weights = pd.DataFrame(
    [(context.split('.')[0], weights_data['contexts'][context]['weight']) for context in weights_data['contexts']],
    columns=['menu', 'weight']
)
menu_weights_dict = df_menu_weights.groupby('menu').mean().to_dict(orient='index')

#%%

data = OrderedDict()
for menu in df_chart_order['menu'].unique():
    menu_key = f"{menu}: {round(menu_weights_dict[menu]['weight']*1,2)}%"
    data[menu_key] = dict()
    for context in df_chart_order['context'].unique():
        if context.startswith(menu):
            context_key = f"{context}: {round(weights_data['contexts'][context]['weight']*1,2)}%"
            data[menu_key][context_key] = dict()
            for chart in df_chart_order[df_chart_order['context'] == context]['chart'].unique():
                chart_key = f"{chart}: {round(weights_data['contexts'][context]['charts'][chart]['weight'],2)}%"
                data[menu_key][context_key][chart_key] = dict()
                for dim in weights_data['contexts'][context]['charts'][chart]['dimensions']:
                    dim_key = dim
                    data[menu_key][context_key][chart_key][dim_key] = f"{round(weights_data['contexts'][context]['charts'][chart]['dimensions'][dim]*1, 2)}%"

st.json(
    data,
    expanded=False
)
