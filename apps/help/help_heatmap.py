# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_CHARTS_REGEX, \
    DEFAULT_HELP_INPUTS_AFTER, DEFAULT_HELP_INPUTS_BEFORE, DEFAULT_HELP_INPUTS_OPTIONS, DEFAULT_HELP_IMAGE_URL_HEATMAP
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Clustered Heatmap
Make a heatmap and cluster similar rows together to make it pretty.  

#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- {DEFAULT_HELP_INPUTS_CHARTS_REGEX}
- {DEFAULT_HELP_INPUTS_AFTER}
- {DEFAULT_HELP_INPUTS_BEFORE}
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs  
##### Clustered Heatmap  
Heatmap of each metric, ordered after clustering.

![image info]({DEFAULT_HELP_IMAGE_URL_HEATMAP})

#### Notes
- Heatmap rows are ordered according to [AgglomerativeClustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html) from [scikit-learn](https://scikit-learn.org/stable/index.html).
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/heatmap"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

