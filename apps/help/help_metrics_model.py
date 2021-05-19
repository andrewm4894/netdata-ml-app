# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_AFTER, DEFAULT_HELP_INPUTS_BEFORE, \
    DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Metrics Model
Build a model for your target metric and see what other metrics are most predictive.
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- **`target metric`** - the metric you want to build a model for.
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs
##### Results
Line plots of the target metric and its most predictive metrics, along with the r-square of the model.

#### Notes
- We use a random forest model from [scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html).
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

