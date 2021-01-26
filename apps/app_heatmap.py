# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from netdata_pandas.data import get_data
from sklearn.cluster import AgglomerativeClustering

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, empty_fig
from .utils.utils import process_opts

DEFAULT_OPTS = 'freq=30s,w=1200'
DEFAULT_CHARTS_REGEX = 'system.*|apps.*|users.*|groups.*'
DEFAULT_CHARTS_REGEX = 'system.*'

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='hm-btn-run', n_clicks=0),
    ]
))
inputs_host = dbc.FormGroup(
    [
        dbc.Label('host', id='hm-label-host', html_for='hm-input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='hm-input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='hm-label-host')
    ]
)
inputs_charts_regex = dbc.FormGroup(
    [
        dbc.Label('charts regex', id='hm-label-charts-regex', html_for='hm-input-charts-regex', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='hm-input-charts-regex', value=DEFAULT_CHARTS_REGEX, type='text', placeholder='system.*'),
        #dbc.Input(id='hm-input-charts-regex', value='.*', type='text', placeholder='system.*'),
        dbc.Tooltip('Regex for charts to pull.', target='hm-label-charts-regex')
    ]
)
inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='hm-label-after', html_for='hm-input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='hm-input-after', value=-1800, type='number', placeholder=-1800),
        dbc.Tooltip('"after" as per netdata rest api.', target='hm-label-after')
    ]
)
inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='hm-label-before', html_for='hm-input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='hm-input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='hm-label-before')
    ]
)
inputs_opts = dbc.FormGroup(
    [
        dbc.Label('options', id='hm-label-opts', html_for='hm-input-opts', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='hm-input-opts', value=DEFAULT_OPTS, type='text', placeholder=DEFAULT_OPTS),
        dbc.Tooltip('list of key values to pass to underlying code.', target='hm-label-opts')
    ]
)
inputs = dbc.Row(
    [
        dbc.Col(inputs_host, width=3),
        dbc.Col(inputs_charts_regex, width=2),
        dbc.Col(inputs_after, width=2),
        dbc.Col(inputs_before, width=2),
        dbc.Col(inputs_opts, width=2),
    ], style={'margin': '0px', 'padding': '0px'}
)
tabs = dbc.Tabs(
    [
        dbc.Tab(label='Clustered Heatmap', id='hm-id-tab-centers', tab_id='hm-tab-centers'),
    ], id='hm-tabs', active_tab='hm-tab-centers', style={'margin': '12px', 'padding': '2px'}
)
layout = html.Div(
    [
        logo,
        main_menu,
        inputs,
        tabs,
        dbc.Spinner(children=[html.Div(children=html.Div(id='hm-figs'))]),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('hm-figs', 'children'),
    Input('hm-btn-run', 'n_clicks'),
    Input('hm-tabs', 'active_tab'),
    State('hm-input-host', 'value'),
    State('hm-input-charts-regex', 'value'),
    State('hm-input-after', 'value'),
    State('hm-input-before', 'value'),
    State('hm-input-opts', 'value'),
)
def run(n_clicks, tab, host, charts_regex, after, before, opts, freq='10s', w='1200'):

    figs = []

    opts = process_opts(opts)
    freq = opts.get('freq', freq)
    w = int(opts.get('w', w))

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cp-fig', figure=empty_fig)))
        return figs

    else:

        # get data
        df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
        # lets resample to a specific frequency
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

        fig = px.imshow(df.transpose(), color_continuous_scale='Greens')
        fig.update_layout(
            autosize=False,
            width=w,
            height=len(df.columns)*20)
        figs.append(html.Div(dcc.Graph(id='hm-fig', figure=fig)))

    return figs

