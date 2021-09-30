# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_METRICS, DEFAULT_HELP_INPUTS_AFTER, \
    DEFAULT_HELP_INPUTS_BEFORE, DEFAULT_HELP_INPUTS_OPTIONS, DEFAULT_HELP_INPUTS_NETDATA_URL
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Anomaly Events
Given a netdata url during which there are anomaly events, loop over each anomaly event, plot its heatmap and the raw metric and corresponding anomaly bit's individually.  
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_METRICS}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}
- {DEFAULT_HELP_INPUTS_NETDATA_URL}

#### Outputs
##### Heatmap  
A heatmap of top `hm_top_n` dimensions that are part of the anomaly event.   

##### Lines  
For each of the `ln_top_n` dimensions in the anomaly event plot the raw data and corresponding anomaly bit.

#### Notes
- For the line plots a buffer period of `start_buffer` * `anomaly_len` is included before the anomaly event.
- For the line plots a buffer period of `end_buffer` * `anomaly_len` is included after the anomaly event.
- Each line plot 
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/anomaly-events"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

