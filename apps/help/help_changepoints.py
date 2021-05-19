# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_AFTER, DEFAULT_HELP_INPUTS_BEFORE, \
    DEFAULT_HELP_INPUTS_OPTIONS, DEFAULT_HELP_INPUTS_CHARTS_REGEX
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Changepoints
Use ML to find some [changepoints](https://en.wikipedia.org/wiki/Change_detection#:~:text=In%20statistical%20analysis%2C%20change%20detection,process%20or%20time%20series%20changes.) in your metrics.  

#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_CHARTS_REGEX}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs  
##### Changepoints  
Plots of the top N changepoints found.

#### Notes
- The [ruptures](https://centre-borelli.github.io/ruptures-docs/) library is used by the app.
- The default algorithim used is [`Window`](https://centre-borelli.github.io/ruptures-docs/code-reference/detection/window-reference/).
- The more included by `chart regex` the longer it will take to process all the data.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/changepoints"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

