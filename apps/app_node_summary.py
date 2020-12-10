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

layout = html.Div([
    html.Div([
        dbc.Button('Home', href='/apps'),
        dbc.Button('Refresh', id='btn-refresh', n_clicks=0),
    ]),
    html.H3('Node Summary'),
    dbc.FormGroup(
        [
            dbc.Label("Host", html_for="input-host", width=1),
            dbc.Col(dbc.Input(id='input-host', value='london.my-netdata.io', type='text', placeholder='host'), width=4),
        ],
        row=True
    ),
    dbc.FormGroup(
        [
            dbc.Label("n", html_for="input-n", width=1),
            dbc.Col(dbc.Input(id='input-n', value=60, type='number', placeholder='n'), width=4),
        ],
        row=True
    ),

    dbc.Tabs(
        [
            dbc.Tab(label='Grid', tab_id='tab-grid'),
            dbc.Tab(label='Lines', tab_id='tab-lines'),
        ],
        id='tabs',
        active_tab='tab-grid'
    ),
    dbc.CardBody(dcc.Graph(id='fig'))
])


@app.callback(
    Output('fig', 'figure'),
    Input('btn-refresh', 'n_clicks'),
    Input('tabs', 'active_tab'),
    State('input-host', 'value'),
    State('input-n', 'value'),
)
def display_value(n_clicks, tab, host, n):
    df = get_data([host], ['system.cpu', 'system.load'], after=-int(n), before=0)
    if tab == 'tab-grid':
        fig = plot_lines_grid(df, return_p=True, show_p=False)
    else:
        fig = plot_lines(df, return_p=True, show_p=False)

    return fig

