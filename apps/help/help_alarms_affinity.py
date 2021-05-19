# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from apps.core.help.defaults import DEFAULT_HELP_INPUTS_HOST, DEFAULT_HELP_INPUTS_OPTIONS
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE

help_body = f"""
## Alarms Affinity
Apply market basket analysis to your alarms to see which alarms/charts co-occur in interesting ways.  

#### Inputs
- {DEFAULT_HELP_INPUTS_HOST}
- **hours ago**: Limit to alarms from last n hours ago.
- **last n**: Limit to alarms from last n alarms.
- {DEFAULT_HELP_INPUTS_OPTIONS}

#### Outputs  
The main outputs on each tab are tables of sets of items or rules between such sets.
##### Alarm Itemsets  
A table showing with sets of alarms tend to occur together.  
##### Alarm Rules  
Association rules found between alarm itemsets.
##### Chart Itemsets  
A table showing with sets of charts tend to occur together.  
##### Chart Rules  
Association rules found between chart itemsets.  

#### Notes
- We use [mlextend](http://rasbt.github.io/mlxtend) [fpgrowth](http://rasbt.github.io/mlxtend/api_subpackages/mlxtend.frequent_patterns/#fpgrowth) and [association_rules](http://rasbt.github.io/mlxtend/api_subpackages/mlxtend.frequent_patterns/#association_rules) algorithims to find itemsets and rulesets.
"""

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button("Back", href="/alarms-affinity"),
    ]
))
layout = html.Div(
    [
        logo,
        main_menu,
        html.Div([dcc.Markdown(help_body)], style={"margin": "8px", "padding": "8px"})
    ], style=DEFAULT_STYLE
)

