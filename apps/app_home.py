# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H3('Home'),
    html.Div([dcc.Link('Go to Node Summary', href='/apps/app_node_summary')]),
    html.Div([dcc.Link('Go to App 2', href='/apps/app2')]),
])
