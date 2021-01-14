# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from netdata_pandas.data import get_data
from sklearn.cluster import AgglomerativeClustering

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, empty_fig


main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='btn-run', n_clicks=0),
    ]
))

inputs_host = dbc.FormGroup(
    [
        dbc.Label('Host', id='label-host', html_for='input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='label-host')
    ]
)

inputs_charts_regex = dbc.FormGroup(
    [
        dbc.Label('Charts Regex', id='label-charts-regex', html_for='input-charts-regex', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-charts-regex', value='system.*', type='text', placeholder='system.*'),
        dbc.Tooltip('Regex for charts to pull.', target='label-charts-regex')
    ]
)

inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='label-after', html_for='input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-after', value=-900, type='number', placeholder=-900),
        dbc.Tooltip('"after" as per netdata rest api.', target='label-after')
    ]
)

inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='label-before', html_for='input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='label-before')
    ]
)

inputs_freq = dbc.FormGroup(
    [
        dbc.Label('freq', id='label-freq', html_for='input-freq', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-freq', value='10s', type='text', placeholder='10s'),
        dbc.Tooltip('Frequency to resample data to, e.g. 10s = 10 seconds.', target='label-freq')
    ]
)

inputs = dbc.Row(
    [
        dbc.Col(inputs_host, width=3),
        dbc.Col(inputs_charts_regex, width=3),
        dbc.Col(inputs_after, width=2),
        dbc.Col(inputs_before, width=2),
        dbc.Col(inputs_freq, width=1),
        dbc.Col(html.Div(''), width=1)
    ], style={'margin': '0px', 'padding': '0px'}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(label='Heatmap', tab_id='tab-heatmap'),
    ], id='tabs', active_tab='tab-heatmap', style={'margin': '12px', 'padding': '2px'}
)

top_card = dbc.CardBody(dcc.Graph(id='fig-heatmap'))

layout = html.Div(
    [
        logo,
        main_menu,
        inputs,
        tabs,
        top_card
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('fig-heatmap', 'figure'),
    Input('btn-run', 'n_clicks'),
    Input('tabs', 'active_tab'),
    State('input-host', 'value'),
    State('input-charts-regex', 'value'),
    State('input-after', 'value'),
    State('input-before', 'value'),
    State('input-freq', 'value'),
)
def display_value(n_clicks, tab, host, charts_regex, after, before, freq):

    # get data
    df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
    # lets resample to 5 sec frequency
    df = df.resample(freq).mean()
    # lets min-max normalize our data so metrics can be compared on a heatmap
    df = (df - df.min()) / (df.max() - df.min())
    # drop na cols
    df = df.dropna(how='all', axis=1)
    # lets do some clustering to sort similar cols
    clustering = AgglomerativeClustering(
        n_clusters=int(round(len(df.columns) * 0.2, 0))
    ).fit(df.fillna(0).transpose().values)
    # get order of cols from the cluster labels
    cols_sorted = pd.DataFrame(
        zip(df.columns, clustering.labels_),
        columns=['metric', 'cluster']
    ).sort_values('cluster')['metric'].values.tolist()
    # re-order cols
    df = df[cols_sorted]
    if n_clicks > 0:
        fig = px.imshow(df.transpose(), color_continuous_scale='Greens')
        fig.update_layout(
            autosize=False,
            width=1200,
            height=1200)
    else:
        fig = empty_fig

    return fig

