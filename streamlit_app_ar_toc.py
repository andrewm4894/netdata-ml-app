
import requests
import pandas as pd
import numpy as np
from netdata_pandas.data import get_data
import matplotlib.pyplot as plt
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

weights_data = requests.get(url_weights).json()

data = OrderedDict()
for context in weights_data['contexts']:
    context_key = f"{context}: {round(weights_data['contexts'][context]['weight'],2)}"
    data[context_key] = dict()
    for chart in weights_data['contexts'][context]['charts']:
        chart_key = f"{chart}: {round(weights_data['contexts'][context]['charts'][chart]['weight'],2)}"
        data[context_key][chart_key] = dict()
        for dim in weights_data['contexts'][context]['charts'][chart]['dimensions']:
            dim_key = dim
            data[context_key][chart_key][dim_key] = round(weights_data['contexts'][context]['charts'][chart]['dimensions'][dim], 2)

st.json(
    data,
    expanded=False
)
