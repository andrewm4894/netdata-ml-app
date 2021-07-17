# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
from dotenv import load_dotenv
load_dotenv()

from app import app
from apps import (
    app_home, app_clustering, app_heatmap, app_percentiles,
    app_alarms_affinity, app_changepoints, app_metrics_explorer,
    app_correlations, app_anomalies, app_mp_anomalies, app_metrics_model, app_anomaly_bit
)
from apps.help import (
    help_metrics_model, help_alarms_affinity, help_anomalies, help_changepoints, help_clustering,
    help_correlations, help_heatmap, help_metrics_explorer, help_mp_anomalies, help_percentiles, help_anomaly_bit
)

server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    # app pages
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
    elif pathname == '/correlations':
        return app_correlations.layout
    elif pathname == '/anomalies':
        return app_anomalies.layout
    elif pathname == '/mp-anomalies':
        return app_mp_anomalies.layout
    elif pathname == '/metrics-model':
        return app_metrics_model.layout
    elif pathname == '/anomaly-bit':
        return app_anomaly_bit.layout
    # home
    elif pathname == '/':
        return app_home.layout
    # help pages
    elif pathname == '/heatmap-help':
        return help_heatmap.layout
    elif pathname == '/changepoints-help':
        return help_changepoints.layout
    elif pathname == '/metrics-explorer-help':
        return help_metrics_explorer.layout
    elif pathname == '/percentiles-help':
        return help_percentiles.layout
    elif pathname == '/alarms-affinity-help':
        return help_alarms_affinity.layout
    elif pathname == '/clustering-help':
        return help_clustering.layout
    elif pathname == '/correlations-help':
        return help_correlations.layout
    elif pathname == '/anomalies-help':
        return help_anomalies.layout
    elif pathname == '/mp-anomalies-help':
        return help_mp_anomalies.layout
    elif pathname == '/metrics-model-help':
        return help_metrics_model.layout
    elif pathname == '/anomaly-bit-help':
        return help_anomaly_bit.layout
    # 404
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(port=os.getenv('PORT', 29999))
