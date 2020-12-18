# -*- coding: utf-8 -*-

import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as dhc
from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE


main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Time Series Clustering', href='/clustering'),
        dbc.Button('Metrics Heatmap', href='/heatmap'),
        dbc.Button('Metric Percentiles', href='/percentiles')
    ], vertical=True
))

layout = html.Div(
    [
        logo,
        main_menu,
    ], style=DEFAULT_STYLE
)
