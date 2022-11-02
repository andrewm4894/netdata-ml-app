
import pandas as pd
import streamlit as st
from urllib.parse import urlparse
import re
from netdata_pandas.data import get_data
from sklearn.decomposition import PCA
from scipy import spatial
from datetime import datetime


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
charts_regex = st.text_input('charts_regex', value='system.*')
n_lag = int(st.number_input('n_lag', value=5))
n_components = int(st.number_input('n_components', value=1))


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

df = get_data(hosts=host, after=baseline_after, before=highlight_before, charts_regex=charts_regex).ffill().fillna(0)
print(df.shape)

#%%

df_baseline = df.loc[baseline_after:baseline_before]
print(df_baseline.shape)

df_highlight = df.loc[highlight_after:highlight_before]
print(df_highlight.shape)

#%%

reconstruction_similarity = []

# loop over each metric
for col in df_highlight.columns:

    # preprocess baseline and highlight data
    # take differences
    # add lags
    X_baseline = pd.concat([df_baseline[col].diff().shift(n) for n in range(0, n_lag + 1)], axis=1).dropna().values
    X_highlight = pd.concat([df_highlight[col].diff().shift(n) for n in range(0, n_lag + 1)], axis=1).dropna().values

    # create pca
    pca = PCA(n_components=n_components)

    # fit pca based on preprocessed baseline data
    pca.fit(X_baseline)

    # use fitted pca to reconstruct the preprocessed highlight data
    X_highlight_reconstructed = pca.inverse_transform(pca.transform(X_highlight))

    # calculate the cosine similarity between the preprocessed highlight data and its reconstruction using the PCA fitted above.
    # metrics that have changed the most between the baseline and highlight window will have a lower quality reconstruction and so lower cosine similarity value
    cosine_similarity = 1 - spatial.distance.cosine(
        X_highlight_reconstructed.reshape(X_highlight_reconstructed.size),
        X_highlight.reshape(X_highlight.size)
    )
    reconstruction_similarity.append([col, cosine_similarity])

# sort to have lowest cosine similarity dims as those that look like they have changed the most.
df_reconstruction_similarity = pd.DataFrame(reconstruction_similarity, columns=['dim', 'cosine_similarity'])
df_reconstruction_similarity = df_reconstruction_similarity.sort_values('cosine_similarity', ascending=True)
df_reconstruction_similarity = df_reconstruction_similarity.set_index('dim')

#%%

#%%

# plot the dims that have changed the most first
for i, row in df_reconstruction_similarity.iterrows():
    msg = f"{i}, {row['cosine_similarity']}"
    #print(msg)
    st.text(msg)
    st.line_chart(df[[i]])

print('done')

#%%
