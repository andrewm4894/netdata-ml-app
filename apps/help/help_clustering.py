# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_CHARTS_REGEX, \
    DEFAULT_HELP_INPUTS_AFTER, DEFAULT_HELP_INPUTS_BEFORE, DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Clustering
Perform time series clustering on metrics to 'group' similar looking metrics together.  
#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_CHARTS_REGEX}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs  
##### Cluster Centers  
A line plot showing the cluster centers for each cluster. The aim here is to give a feel for the 'shape' of each cluster.  
##### Cluster Details  
For each cluster plot each metric that is a part of it, ordered by cluster quality score.  

#### Notes
- We use [TimeSeriesKMeans](https://tslearn.readthedocs.io/en/stable/gen_modules/clustering/tslearn.clustering.TimeSeriesKMeans.html) from [tslearn](https://tslearn.readthedocs.io/en/stable/index.html) to do the clustering.
- For each cluster we compute a "quality score" which is based on the average correlation between all cluster metrics, a higher value should imply a 'tighter' clustering.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/clustering"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

