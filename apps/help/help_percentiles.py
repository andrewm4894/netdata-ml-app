# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_METRICS, DEFAULT_HELP_INPUTS_AFTER, \
    DEFAULT_HELP_INPUTS_BEFORE, DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Percentiles
Use a reference window to work out metric percentiles and find metrics with highest "crossover rate".  
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_METRICS}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs  
##### Percentiles 
A typical line plot but with horizontal lines added for key percentiles based on the reference window used.  

![image info]({DEFAULT_HELP_IMAGE_URL_PERCENTILES})

#### Notes
- Hover over each vertical line to see what percentile it represents.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/percentiles"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

