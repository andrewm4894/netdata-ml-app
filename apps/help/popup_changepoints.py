# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

app_prefix = 'cp'

help_body = """
Use ML to find some [changepoints](https://en.wikipedia.org/wiki/Change_detection#:~:text=In%20statistical%20analysis%2C%20change%20detection,process%20or%20time%20series%20changes.) in your metrics.  
###### Changepoints  
The app will run the [`window`](https://centre-borelli.github.io/ruptures-docs/code-reference/detection/window-reference/) \
algorithm for changepoint detection on each metric defined by the `charts regex` input.  

Changes found will be ranked and plotted per metric with the region of change highlighted.
"""

help = html.Div([
    dbc.Modal([
        dbc.ModalHeader("Changepoint Detection"),
        dbc.ModalBody(dcc.Markdown(help_body)),
        dbc.ModalFooter(
            dbc.ButtonGroup(
                [
                    dbc.Button("More Help!", href="/changepoints-help"),
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
