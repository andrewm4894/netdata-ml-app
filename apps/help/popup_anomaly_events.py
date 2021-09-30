# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

help_body = """
xxx.  
  
###### Lines  
xxx.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Anomaly Events"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup([dbc.Button("More Help!", href="/anomaly-events-help"), dbc.Button("Close", id="ae-help-close", className="ml-auto")])
    ),
    ], id="ae-modal")]
)


@app.callback(
    Output("ae-modal", "is_open"),
    [Input("ae-help-open", "n_clicks"),
     Input("ae-help-close", "n_clicks")],
    [State("ae-modal", "is_open")],
)
def toggle_help(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
