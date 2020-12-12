# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from netdata_pandas.data import get_data
from am4894plots.plots import plot_lines, plot_lines_grid

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE


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

inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='label-after', html_for='input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-after', value=-60, type='number', placeholder=-60),
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

inputs_num_clusters = dbc.FormGroup(
    [
        dbc.Label('k', id='label-num-clusters', html_for='input-num-clusters', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-num-clusters', value=20, type='number', placeholder=20),
        dbc.Tooltip('The number of clusters to form.', target='label-num-clusters')
    ]
)

inputs = dbc.Row(
    [
        dbc.Col(inputs_host, width=3),
        dbc.Col(inputs_after, width=2),
        dbc.Col(inputs_before, width=2),
        dbc.Col(inputs_num_clusters, width=1),
        dbc.Col(html.Div(''), width=4)
    ], style={'margin': '0px', 'padding': '0px'}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(label='Cluster Centers', tab_id='tab-centers'),
        dbc.Tab(label='Cluster Details', tab_id='tab-details'),
    ], id='tabs', active_tab='tab-centers', style={'margin': '12px', 'padding': '2px'}
)

top_card = dbc.CardBody(dcc.Graph(id='fig-affinity'))

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
    Output('fig-affinity', 'figure'),
    Input('btn-run', 'n_clicks'),
    Input('tabs', 'active_tab'),
    State('input-host', 'value'),
    State('input-after', 'value'),
    State('input-before', 'value'),
    State('input-num-clusters', 'value'),
)
def display_value(n_clicks, tab, host, after, before, k):
    df = get_data([host], ['system.cpu', 'system.load', 'system.net'], after=int(after), before=int(after))
    if tab == 'tab-centers':
        fig = plot_lines_grid(df, return_p=True, show_p=False, h=1200)
    else:
        fig = plot_lines(df, return_p=True, show_p=False, h=1200)

    return fig

