# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

app_prefix = 'cor'

help_body = """
Perform various correlation based analysis on each pair of metrics.  
###### Correlation Heatmap  
A heatmap of all pairwise correlations.  
###### Correlation Barplot  
A bar plot showing top correlations, green for positive, red for negative.
###### Correlation Changes  
A scatter plot and table of correlation before vs after the selected window, to show what pairs of metrics have changed most recently in terms of their correlation.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Correlations"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup(
                [
                    dbc.Button("More Help!", href="/correlations-help"),
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
