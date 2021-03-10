# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

help_body = """
TODO  
  
###### TODO  
todo.  
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Clustered Heatmap"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup([dbc.Button("More Help!", href="/heatmap-help"), dbc.Button("Close", id="hm-help-close", className="ml-auto")])
    ),
    ], id="hm-modal")]
)


@app.callback(
    Output("hm-modal", "is_open"),
    [Input("hm-help-open", "n_clicks"),
     Input("hm-help-close", "n_clicks")],
    [State("hm-modal", "is_open")],
)
def toggle_help(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
