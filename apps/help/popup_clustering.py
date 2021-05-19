# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

app_prefix = 'cl'

help_body = """
Perform time series clustering on metrics to 'group' similar looking metrics together.  
###### Cluster Centers  
A line plot showing the cluster centers for each cluster. The aim here is to give a feel for the 'shape' of each cluster.  
###### Cluster Details  
For each cluster plot each metric that is a part of it, ordered by cluster quality score.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Time Series Clustering"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup(
                [
                    dbc.Button("More Help!", href="/clustering-help"),
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
