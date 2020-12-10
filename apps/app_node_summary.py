# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from netdata_pandas.data import get_data
from am4894plots.plots import plot_lines, plot_lines_grid

from app import app

layout = html.Div([
    dcc.Link('Home', href='/apps'),
    html.H3('Node Summary'),
    dcc.Input(id='input-host', value='london.my-netdata.io', type='text', placeholder='host'),
    dcc.Input(id='input-n', value=60, type='number', placeholder='n'),
    html.Button('Refresh', id='btn-refresh', n_clicks=0),
    dcc.Tabs(id='tabs', value='tab-grid', children=[
        dcc.Tab(label='Grid', value='tab-grid'),
        dcc.Tab(label='Lines', value='tab-lines'),
    ]),
    dcc.Graph(id='fig')
])


@app.callback(
    Output('fig', 'figure'),
    Input('btn-refresh', 'n_clicks'),
    Input('tabs', 'value'),
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

