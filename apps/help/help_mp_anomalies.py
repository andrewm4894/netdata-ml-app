# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_CHARTS_REGEX, \
    DEFAULT_HELP_INPUTS_AFTER, DEFAULT_HELP_INPUTS_BEFORE, DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Matrix Profile Anomalies
Compute the "[Matrix Profile](https://matrixprofile.org/#:~:text=The%20matrix%20profile%20is%20a,scalable%20and%20largely%20parameter%2Dfree.)" for each metric and use it to rank the most anomalous metrics.
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_CHARTS_REGEX}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs
##### Anomalies
For each metric plot the raw data and the matrix profile underneath it. Where the matrix profile is its highest value corresponds to where it thinks the raw data is most anomalous.

#### Notes
- We use a the [STUMPY](https://stumpy.readthedocs.io/en/latest/index.html) package to calculate the matrix profile.
- [Here](https://andrewm4894.com/2021/02/16/anomaly-detection-using-matrix-profile/) is a blog post that walks though the approach taken in the app.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/mp-anomalies"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

