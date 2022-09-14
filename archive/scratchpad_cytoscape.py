# used for playing with random dev code

#%%

import requests
import pandas as pd
import numpy as np
from apps.core.utils.inputs import parse_netdata_url
from netdata_pandas.data import get_data
import matplotlib.pyplot as plt

netdata_url = 'http://34.139.5.223:19999/#after=1663148557000;before=1663151210000;menu_system;theme=slate;utc=Europe%2FLondon'

url_dict = parse_netdata_url(netdata_url)
host = url_dict['host:port']
after = int(url_dict['fragments']['after'])//1000
before = int(url_dict['fragments']['before'])//1000
highlight_after = int(url_dict['fragments'].get('highlight_after', '0'))//1000
highlight_before = int(url_dict['fragments'].get('highlight_before', '0'))//1000

after = highlight_after if highlight_after > 0 else after
before = highlight_before if highlight_before > 0 else before

print(highlight_after)
print(highlight_before)
print(after)
print(before)


#%%

url_weights = f"http://{host}/api/v1/weights?after={after}&before={before}"
print(url_weights)

weights_data = requests.get(url_weights).json()

#%%

data = []
for context_num, context in enumerate(weights_data['contexts'], 1):
    data.append([context, 'ALL', 'ALL', weights_data['contexts'][context]['weight'], 2, context_num])
    for chart_num, chart in enumerate(weights_data['contexts'][context]['charts'], 1):
        data.append([context, chart, 'ALL', weights_data['contexts'][context]['charts'][chart]['weight'], 3, chart_num])
        for dim_num, dim in enumerate(weights_data['contexts'][context]['charts'][chart]['dimensions'], 1):
            data.append([context, chart, dim, weights_data['contexts'][context]['charts'][chart]['dimensions'][dim], 4, dim_num])

data.append(['ALL', 'ALL', 'ALL', np.mean([d[3] for d in data if d[2] != 'ALL']), 1, 1])

df_weights = pd.DataFrame(data, columns=['context', 'chart', 'dim', 'weight', 'level', 'element'])

print(df_weights)

#%%

df_weights['id'] = df_weights['context'] + '|' + df_weights['chart'] + '|' + df_weights['dim']
df_weights['label'] = df_weights['id'] + ' (' + round(df_weights['weight'], 2).astype(str) + ')'
df_weights['parent_id'] = np.where(df_weights['level'] == 4, df_weights['id'].str.split('|').str[0:2].str.join('|') + '|ALL', '')
df_weights['parent_id'] = np.where(df_weights['level'] == 3, df_weights['id'].str.split('|').str[0:1].str.join('|') + '|ALL|ALL', df_weights['parent_id'])
df_weights['parent_id'] = np.where(df_weights['level'] == 2, 'ALL|ALL|ALL', df_weights['parent_id'])

print(df_weights)

#%%

#%%

#%%

data_elements = []
for i, row in df_weights.iterrows():
    id = row['id']
    label = row['label']
    level = row['level']
    element = row['element']
    x = element * 100
    y = level * 100
    data_element = {
        'data': {'id': id.replace('ALL', ''), 'label': label.replace('ALL', '')},
        #'position': {'x': x, 'y': y}
    }
    data_elements.append(data_element)

#%%

#source_node = df_weights[df_weights['context'] == 'ALL']['id'].values.tolist()[0]
#target_nodes = df_weights[df_weights['chart'] == 'ALL']['id'].values.tolist()
#source_nodes = [source_node for x in range(len(target_nodes))]
#data_elements_edges = [{'data': {'source': x[0], 'target': x[1] }} for x in list(zip(source_nodes, target_nodes))]
data_edges = df_weights[df_weights['parent_id'] != ''][['parent_id', 'id']].values.tolist()
data_elements_edges = [{'data': {'source': x[0].replace('ALL', ''), 'target': x[1].replace('ALL', '')}} for x in data_edges]
data_elements.extend(data_elements_edges)

print(data_elements)

#%%

#%%

#%%

import dash
from dash import dash_table
import dash_cytoscape as cyto
import dash_html_components as html

app = dash.Dash(__name__)

"""
elements=[
            {'data': {'id': 'one', 'label': 'Node A'}, 'position': {'x': 50, 'y': 50}},
            {'data': {'id': 'two', 'label': 'Node B'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'id': 'three', 'label': 'Node C'}, 'position': {'x': 200, 'y': 250}},
            {'data': {'source': 'one', 'target': 'two'}},
            {'data': {'source': 'one', 'target': 'three'}}
        ]
"""
"""
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'breadthfirst'},
        #layout={'name': 'grid'},
        style={'width': '100%', 'height': '400px'},
        elements=data_elements
    )
])
"""

dash_cols = ['context', 'chart', 'dim', 'weight']
app.layout = dash_table.DataTable(
    data=df_weights[dash_cols].to_dict('records'),
    columns=[{"name": i, "id": i} for i in df_weights[dash_cols].columns],
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
)

if __name__ == '__main__':
    app.run_server(debug=True)


#%%