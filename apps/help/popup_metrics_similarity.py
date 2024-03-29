# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

app_prefix = 'ms'

help_body = """
Find most similar looking metrics to your target metric.
###### Results
Line plots of the target metric and its most similar metrics.
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Metrics Similarity"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup([dbc.Button("More Help!", href="/metrics-similarity-help"), dbc.Button("Close", id="ms-help-close", className="ml-auto")])
        #dbc.Button("Close", id="me-help-close", className="ml-auto")
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
