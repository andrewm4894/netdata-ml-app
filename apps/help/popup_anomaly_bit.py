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
        dbc.ModalHeader("Anomaly Bit"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup([dbc.Button("More Help!", href="/anomaly-bit-help"), dbc.Button("Close", id="me-help-close", className="ml-auto")])
    ),
    ], id="ab-modal")]
)


@app.callback(
    Output("ab-modal", "is_open"),
    [Input("ab-help-open", "n_clicks"),
     Input("ab-help-close", "n_clicks")],
    [State("ab-modal", "is_open")],
)
def toggle_help(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
