
import requests
import pandas as pd
import numpy as np
from apps.core.utils.inputs import parse_netdata_url
from netdata_pandas.data import get_data
import matplotlib.pyplot as plt
import streamlit as st
from collections import OrderedDict


netdata_url = st.text_input('netdata_agent_dashboard_url', value='http://london.my-netdata.io/#after=-900000;before=0;=undefined;theme=slate;utc=Europe%2FLondon')

#%%

#netdata_url = 'http://34.139.5.223:19999/#after=1663247360000;before=1663248336000;highlight_after=1663248091134;highlight_before=1663248151591;theme=slate;utc=Europe%2FLondon'

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


#%%

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

#%%
