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

DEFAULT_STYLE = {'margin': '2px', 'padding': '2px'}

logo = dbc.Row(dbc.Col(html.Img(src=app.get_asset_url('netdata-logo.png')), style=DEFAULT_STYLE), style=DEFAULT_STYLE)

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Refresh', id='btn-refresh', n_clicks=0)
    ]
))

inputs_host = dbc.FormGroup(
    [
        dbc.Label("Host", html_for="input-host"),
        dbc.Input(id='input-host', value='london.my-netdata.io', type='text', placeholder='host'),
    ]
)

inputs_n = dbc.FormGroup(
    [
        dbc.Label("n", html_for="input-n"),
        dbc.Input(id='input-n', value=60, type='number', placeholder='n'),
    ]
)

inputs = dbc.Row(
    [dbc.Card([inputs_host, inputs_n], body=True), dbc.Col(html.Div(''), width=9)],
    style={'margin': '12px', 'padding': '2px'}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(label='a', tab_id='tab-a'),
        dbc.Tab(label='b', tab_id='tab-b'),
    ], id='tabs', active_tab='tab-a', style={'margin': '12px', 'padding': '2px'}
)

top_card = dbc.CardBody(dcc.Graph(id='fig'))

layout = html.Div(
    [
        logo,
        html.Br(),
        main_menu,
        inputs,
        tabs,
        top_card
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('fig', 'figure'),
    Input('btn-refresh', 'n_clicks'),
    Input('tabs', 'active_tab'),
    State('input-host', 'value'),
    State('input-n', 'value'),
)
def display_value(n_clicks, tab, host, n):
    df = get_data([host], ['system.cpu', 'system.load'], after=-int(n), before=0)
    if tab == 'tab-a':
        fig = plot_lines_grid(df, return_p=True, show_p=False, h=1200)
    else:
        fig = plot_lines(df, return_p=True, show_p=False, h=1200)

    return fig

