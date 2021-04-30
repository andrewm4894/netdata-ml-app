# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = """
## Metrics Model
xxx

### Inputs
- **host**: host you want to pull data from?
xxx
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/metrics-model"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

