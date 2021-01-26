# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

help_body = """
A brief description  
  
###### Lines  
some info.  

###### Scatters  
some more info.  

###### Histograms  
some more info.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Metrics Explorer"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(dbc.Button("Close", id="me-help-close", className="ml-auto")),
    ], id="me-modal")]
)


@app.callback(
    Output("me-modal", "is_open"),
    [Input("me-help-open", "n_clicks"),
     Input("me-help-close", "n_clicks")],
    [State("me-modal", "is_open")],
)
def toggle_help(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
