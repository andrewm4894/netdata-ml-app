# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_AFTER, DEFAULT_HELP_INPUTS_BEFORE, \
    DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Metrics Similarity
Find what metrics are most similar to a metric of interest.
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- **`target metric`** - the metric you want to find similar metrics to.
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs
##### Results
Top N line plots sorted by similarity to target metric.

#### Notes
- We use cosine similarity.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/metrics-similarity"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

