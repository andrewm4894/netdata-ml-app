# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_CHARTS_REGEX, \
    DEFAULT_HELP_INPUTS_AFTER, DEFAULT_HELP_INPUTS_BEFORE, DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Anomalies
Perform various correlation based analysis on each pair of metrics.
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_CHARTS_REGEX}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs
##### Anomaly Flags
Line graphs of which charts have been flagged as anomalous.
##### Anomaly Probabilities
Line graphs of anomaly probability score per chart.
##### Anomaly Heatmaps
Heatmaps of anomaly flags and probabilities per chart.
##### Charts
Line plots of the raw charts with anomalous regions shaded.

#### Notes
- We use a [PCA](https://pyod.readthedocs.io/en/latest/_modules/pyod/models/pca.html) model from the [PyOD](https://pyod.readthedocs.io/en/latest/index.html) library as the default model for each chart.
- The default training window for the anomaly models is the preceding 4 hours.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/anomalies"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

