# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app

DEFAULT_STYLE = {"margin": "1px", "padding": "1px"}

layout = html.Div(
    [
        html.H3('Netdata ML App'),
        dbc.FormGroup([
            dbc.Col(dbc.Button('Node Summary', href='/apps/app_node_summary', block=True), width=2, style=DEFAULT_STYLE),
            dbc.Col(dbc.Button('App 2', href='/apps/app2', block=True), width=2, style=DEFAULT_STYLE)
        ], style=DEFAULT_STYLE)
    ],
    style=DEFAULT_STYLE
)
