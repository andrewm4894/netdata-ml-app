# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE

help_body = """
## Metrics Explorer
Explore a specific set of metrics.

### Inputs
- **host**: host you want to pull data from?
- **charts**: a string list of specific metrics you want to focus on in the format "chart.name|metric,chart.name|metric", for example "system.cpu|user,system.load|load1".
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Metrics Explorer", href="/metrics-explorer"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

