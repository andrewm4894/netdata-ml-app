# -*- coding: utf-8 -*-

import logging
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as dhc
from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE
from .dev.dev import say_hello


main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Time Series Clustering', href='/clustering'),
        dbc.Button('Metrics Heatmap', href='/heatmap'),
        dbc.Button('Metric Percentiles', href='/percentiles'),
        dbc.Button('Alarms Affinity', href='/alarms-affinity')
    ], vertical=True
))

layout = html.Div(
    [
        logo,
        main_menu,
    ], style=DEFAULT_STYLE
)

logging.info(say_hello())