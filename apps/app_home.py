# -*- coding: utf-8 -*-

import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE
from apps.core.utils.inputs import make_card

# cards
card_metrics_explorer = make_card(
    dbc.Button(dcc.Markdown('`Metrics Explorer`'), href='/metrics-explorer', style={'height': '40px'}, outline=True),
    '`Explore some metrics.`',
    'metrics_explorer_logo.png'
)
card_changepoints = make_card(
    dbc.Button(dcc.Markdown('`Changepoint Detection`'), href='/changepoints', style={'height': '40px'}, outline=True),
    '`Detect "shifts" in metrics.`',
    'changepoint_detection_logo.png'
)
card_heatmap = make_card(
    dbc.Button(dcc.Markdown('`Clustered Heatmap`'), href='/heatmap', style={'height': '40px'}, outline=True),
    '`We all love heatmaps!`',
    'heatmap_logo.png'
)
card_percentiles = make_card(
    dbc.Button(dcc.Markdown('`Metric Percentiles`'), href='/percentiles', style={'height': '40px'}, outline=True),
    '`Add percentile lines to charts.`',
    'percentiles_logo.png'
)
card_alarms_affinity = make_card(
    dbc.Button(dcc.Markdown('`Alarms Affinity`'), href='/alarms-affinity', style={'height': '40px'}, outline=True),
    '`Explore which alarms co-occur.`',
    'alarms_affinity_logo.png'
)
card_clustering = make_card(
    dbc.Button(dcc.Markdown('`Time Series Clustering`'), href='/clustering', style={'height': '40px'}, outline=True),
    '`Find metrics that move together.`',
    'clustering_logo.png'
)
card_correlations = make_card(
    dbc.Button(dcc.Markdown('`Correlations`'), href='/correlations', style={'height': '40px'}, outline=True),
    '`Explore correlations across metrics.`',
    'correlation_logo.png'
)
card_anomalies = make_card(
    dbc.Button(dcc.Markdown('`Anomalies`'), href='/anomalies', style={'height': '40px'}, outline=True),
    '`Anomaly detection using PyOD.`',
    'anomalies_logo.png'
)
card_mp_anomalies = make_card(
    dbc.Button(dcc.Markdown('`Matrix Profile Anomalies`'), href='/mp-anomalies', style={'height': '40px'}, outline=True),
    '`Anomaly detection using Matrix Profile.`',
    'mp_anomalies_logo.png'
)
card_metrics_model = make_card(
    dbc.Button(dcc.Markdown('`Metric Model`'), href='/metrics-model', style={'height': '40px'}, outline=True),
    '`Build a predictive model for a metrics of interest.`',
    'metrics_model_logo.png'
)
cards = dbc.CardColumns([
    card_metrics_explorer,
    card_changepoints,
    card_heatmap,
    card_percentiles,
    card_alarms_affinity,
    card_clustering,
    card_correlations,
    card_anomalies,
    card_mp_anomalies,
    card_metrics_model
], style=DEFAULT_STYLE)

# make layout
layout = html.Div(
    [
        logo,
        cards,
    ], style=DEFAULT_STYLE
)
