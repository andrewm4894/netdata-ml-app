# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

help_body = """
Explore some specific metrics of interest in various ways.  
  
###### Lines  
Time series plots to see metrics over time on the same plot.  

###### Scatters  
Look at scatter plots of all pairs of metrics of interest.  

###### Histograms  
Histograms for each metric.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Metrics Explorer"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup([dbc.Button("More Help!", href="/metrics-explorer-help"), dbc.Button("Close", id="me-help-close", className="ml-auto")])
        #dbc.Button("Close", id="me-help-close", className="ml-auto")
    ),
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
