# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_METRICS, DEFAULT_HELP_INPUTS_AFTER, \
    DEFAULT_HELP_INPUTS_BEFORE, DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Metrics Explorer
Explore a specific set of metrics from across multiple charts.  
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_METRICS}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs
There are 3 tabs with results populated by the app.  
##### Lines  
Time series plots to see metrics over time on the same plot. There is a line plot with all metrics shown and also a \
grid plot that shows each metric stacked into a grid of sparklines.   
##### Scatters  
Look at scatter plots of all pairs of metrics of interest.  
##### Histograms  
Histograms for each metric.  

#### Notes
- You can use the chart legends to further hide or select metrics of interest.
- Double click on a metric in the legend to just show that metric.
- If you are interested in a big window of time then you could use `smooth_n` to smooth the data using a rolling average.
- The more metrics you include the "busier" the charts will end up looking.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/metrics-explorer"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

