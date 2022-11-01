
import pandas as pd
import streamlit as st
from urllib.parse import urlparse
import re
from netdata_pandas.data import get_data
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score
from datetime import datetime
from apps.core.plots.lines import plot_lines


#%%

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
    if child_host:
        url_dict['child_host'] = child_host
        url_dict['host:port'] = url_dict['host:port'] + f'/host/{child_host}'

    return url_dict

#%%

DEFAULT_URL = 'http://london.my-netdata.io/#after=1667311161000;before=1667311581000;menu_system_submenu_cpu=undefined;highlight_after=1667311286150;highlight_before=1667311353146;theme=slate;utc=Europe%2FLondon'
netdata_url = st.text_input('netdata_agent_dashboard_url', value=DEFAULT_URL)


url_dict = parse_netdata_url(netdata_url)
host = url_dict['host:port']
after = int(url_dict['fragments'].get('after', '-900000'))//1000
before = int(url_dict['fragments'].get('before', '0'))//1000
highlight_after = int(url_dict['fragments'].get('highlight_after', '0'))//1000
highlight_before = int(url_dict['fragments'].get('highlight_before', '0'))//1000
window_length = highlight_before - highlight_after
baseline_after = highlight_after - (window_length * 4)
baseline_before = highlight_after

highlight_after_ts = pd.Timestamp(datetime.utcfromtimestamp(highlight_after).strftime('%Y-%m-%d %H:%M:%S'))
highlight_before_ts = pd.Timestamp(datetime.utcfromtimestamp(highlight_before).strftime('%Y-%m-%d %H:%M:%S'))

print(host)
print(baseline_after)
print(baseline_before)
print(highlight_after)
print(highlight_before)


#%%

df = get_data(hosts=host, after=baseline_after, before=highlight_before, charts_regex='apps.cpu*').ffill().fillna(0)
print(df.shape)

#%%

df_baseline = df.loc[baseline_after:baseline_before]
print(df_baseline.shape)

df_highlight = df.loc[highlight_after:highlight_before]
print(df_highlight.shape)

#%%

reconstruction_errors = []
for col in df_highlight.columns:
    X_baseline = df_baseline[[col]].diff().dropna()
    X_highlight = df_highlight[[col]].diff().dropna()
    pca = PCA()
    pca.fit(X_baseline)
    X_highlight_reconstructed = pca.inverse_transform(pca.transform(X_highlight))
    reconstruction_error = 1 - r2_score(X_highlight, X_highlight_reconstructed)
    reconstruction_errors.append([col, reconstruction_error])

df_reconstruction_errors = pd.DataFrame(reconstruction_errors, columns=['dim', 'reconstruction_error'])
df_reconstruction_errors = df_reconstruction_errors.sort_values('reconstruction_error', ascending=False)
df_reconstruction_errors = df_reconstruction_errors.set_index('dim')
#print(df_reconstruction_errors)

#%%

#%%

for i, row in df_reconstruction_errors.iterrows():
    fig = plot_lines(
        df[[i]], title=i, visible_legendonly=False, hide_y_axis=True,
        shade_regions=[(highlight_after_ts, highlight_before_ts, 'grey')]
    )
    st.plotly_chart(fig, use_container_width=True)

#%%
