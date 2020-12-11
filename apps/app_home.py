# -*- coding: utf-8 -*-

import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app

DEFAULT_STYLE = {"margin": "2px", "padding": "2px"}

logo = dbc.Row(dbc.Col(html.Img(src=app.get_asset_url('netdata-logo.png')), style=DEFAULT_STYLE), style=DEFAULT_STYLE)

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Time Series Clustering', href='/clustering'),
        dbc.Button('Alarms Affinity', href='/alarms-affinity')
    ], vertical=True
))

layout = html.Div(
    [
        logo,
        html.Br(),
        main_menu,
    ], style=DEFAULT_STYLE
)
