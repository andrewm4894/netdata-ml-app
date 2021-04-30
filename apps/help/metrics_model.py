# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

help_body = """
blah
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Metrics Model"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup([dbc.Button("More Help!", href="/metrics-model-help"), dbc.Button("Close", id="mm-help-close", className="ml-auto")])
        #dbc.Button("Close", id="me-help-close", className="ml-auto")
    ),
    ], id="mm-modal")]
)


@app.callback(
    Output("mm-modal", "is_open"),
    [Input("mm-help-open", "n_clicks"),
     Input("mm-help-close", "n_clicks")],
    [State("mm-modal", "is_open")],
)
def toggle_help(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
