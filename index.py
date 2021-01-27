# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import (
    app_home, app_clustering, app_heatmap, app_percentiles,
    app_alarms_affinity, app_changepoints, app_metrics_explorer,
    help_metrics_explorer
)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/clustering':
        return app_clustering.layout
    elif pathname == '/heatmap':
        return app_heatmap.layout
    elif pathname == '/percentiles':
        return app_percentiles.layout
    elif pathname == '/alarms-affinity':
        return app_alarms_affinity.layout
    elif pathname == '/changepoints':
        return app_changepoints.layout
    elif pathname == '/metrics-explorer':
        return app_metrics_explorer.layout
    elif pathname == '/metrics-explorer-help':
        return help_metrics_explorer.layout
    elif pathname == '/':
        return app_home.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
