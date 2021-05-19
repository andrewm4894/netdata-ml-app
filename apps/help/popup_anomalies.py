# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

app_prefix = 'ad'

help_body = """
Perform various correlation based analysis on each pair of metrics.
###### Anomaly Flags
Line graphs of which charts have been flagged as anomalous.
###### Anomaly Probabilities
Line graphs of anomaly probability score per chart.
###### Anomaly Heatmaps
Heatmaps of anomaly flags and probabilities per chart.
###### Charts
Line plots of the raw charts with anomalous regions shaded.
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Anomalies"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup(
                [
                    dbc.Button("More Help!", href="/anomalies-help"),
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
