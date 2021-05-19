# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

app_prefix = 'al'

help_body = """
Apply market basket analysis to your alarms to see which alarms/charts co-occur in interesting ways.  

###### Alarm Itemsets  
A table showing with sets of alarms tend to occur together.  
###### Alarm Rules  
Association rules found between alarm itemsets.
###### Chart Itemsets  
A table showing with sets of charts tend to occur together.  
###### Chart Rules  
Association rules found between chart itemsets.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Alarms Affinity"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup(
                [
                    dbc.Button("More Help!", href="/alarms-affinity-help"),
                    dbc.Button("Close", id=f"{app_prefix}-help-close", className="ml-auto")
                ]
            )
        ),
    ], id=f"{app_prefix}-modal")]
)


@app.callback(
    Output(f"{app_prefix}-modal", "is_open"),
    [Input(f"{app_prefix}-help-open", "n_clicks"),
     Input(f"{app_prefix}-help-close", "n_clicks")],
    [State(f"{app_prefix}-modal", "is_open")],
)
def toggle_help(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
