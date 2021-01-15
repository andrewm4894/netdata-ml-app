# -*- coding: utf-8 -*-

import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE


# create buttons
button_style = dict(width='500px', textAlign='center', height='40px')
button_outline = True
button_clustering = dbc.Button(dcc.Markdown('**Time Series Clustering** - Find metrics that move together ([docs](https://www.netdata.cloud/))'), href='/clustering', outline=button_outline, style=button_style)
button_heatmap = dbc.Button(dcc.Markdown('**Metrics Heatmap** - We all love heatmaps! ([docs](https://www.netdata.cloud/))'), href='/heatmap', outline=button_outline, style=button_style)
button_percentiles = dbc.Button(dcc.Markdown('**Metric Percentiles** - Add percentile lines to charts ([docs](https://www.netdata.cloud/))'), href='/percentiles', outline=button_outline, style=button_style)
button_alarms_affinity = dbc.Button(dcc.Markdown('**Alarms Affinity** - Explore which alarms co-occur ([docs](https://www.netdata.cloud/))'), href='/alarms-affinity', outline=button_outline, style=button_style)
button_changepoints = dbc.Button(dcc.Markdown('**Changepoint Detection** - Detect "shifts" in metrics ([docs](https://www.netdata.cloud/))'), href='/changepoints', outline=button_outline, style=button_style)
button_div_style = dict(marginLeft='15px')

# make layout
layout = html.Div(
    [
        logo,
        html.Div(button_clustering, style=button_div_style),
        html.Div(button_heatmap, style=button_div_style),
        html.Div(button_percentiles, style=button_div_style),
        html.Div(button_alarms_affinity, style=button_div_style),
        html.Div(button_changepoints, style=button_div_style),
    ], style=DEFAULT_STYLE
)
