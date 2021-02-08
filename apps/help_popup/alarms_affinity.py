# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

help_body = """
A brief description  
  
###### Alarm Itemsets  
some info.  

###### Alarm Rules  
some more info.  

###### Chart Itemsets  
some more info.  

###### Chart Rules  
some more info.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Alarms Affinity"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(dbc.Button("Close", id="al-help-close", className="ml-auto")),
    ], id="al-modal")]
)


@app.callback(
    Output("al-modal", "is_open"),
    [Input("al-help-open", "n_clicks"), Input("al-help-close", "n_clicks")],
    [State("al-modal", "is_open")],
)
def toggle_help(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
