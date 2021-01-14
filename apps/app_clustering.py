# -*- coding: utf-8 -*-

import logging
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
from netdata_pandas.data import get_data, get_chart_list
from am4894plots.plots import plot_lines, plot_lines_grid
from netdata_ts_clustering.core import Clusterer

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE


main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='btn-run', n_clicks=0),
    ]
))

inputs_host = dbc.FormGroup(
    [
        dbc.Label('Host', id='label-host', html_for='input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='label-host')
    ]
)

inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='label-after', html_for='input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-after', value=-900, type='number', placeholder=-900),
        dbc.Tooltip('"after" as per netdata rest api.', target='label-after')
    ]
)

inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='label-before', html_for='input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='label-before')
    ]
)

inputs_num_clusters = dbc.FormGroup(
    [
        dbc.Label('k', id='label-num-clusters', html_for='input-num-clusters', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-num-clusters', value=20, type='number', placeholder=20),
        dbc.Tooltip('The number of clusters to form.', target='label-num-clusters')
    ]
)

inputs = dbc.Row(
    [
        dbc.Col(inputs_host, width=3),
        dbc.Col(inputs_after, width=2),
        dbc.Col(inputs_before, width=2),
        dbc.Col(inputs_num_clusters, width=1),
        dbc.Col(html.Div(''), width=4)
    ], style={'margin': '0px', 'padding': '0px'}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(label='Cluster Centers', id='id-tab-centers', tab_id='tab-centers'),
        dbc.Tab(label='Cluster Details', id='id-tab-details', tab_id='tab-details'),
    ], id='tabs', active_tab='tab-centers', style={'margin': '12px', 'padding': '2px'}
)

layout = html.Div(
    [
        logo,
        main_menu,
        inputs,
        tabs,
        html.Div(children=html.Div(id='figs')),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('figs', 'children'),
    Input('btn-run', 'n_clicks'),
    Input('tabs', 'active_tab'),
    State('input-host', 'value'),
    State('input-after', 'value'),
    State('input-before', 'value'),
    State('input-num-clusters', 'value')
)
def get_plots(n_clicks, tab, host, after, before, k):
    ctx = dash.callback_context

    global states_previous
    global states_current
    global model
    global valid_clusters
    states_current = ctx.states

    def run_model(host, after, before, k):
        charts = get_chart_list(host)
        model = Clusterer([host], charts=charts, after=after, before=before, n_clusters=k)
        model.run_all()
        valid_clusters = model.df_cluster_meta[model.df_cluster_meta['valid'] == 1].index
        return model, valid_clusters

    if 'states_previous' in globals():
        if set(states_previous.values()) != set(states_current.values()):
            model, valid_clusters = run_model(host, after, before, k)
    else:
        model, valid_clusters = run_model(host, after, before, k)

    figs = []
    if tab == 'tab-centers':
        # plot centers
        titles = [f'{int(x[0])} - n={int(x[1])}, qs={x[2]}' for x in
                  model.df_cluster_meta.loc[valid_clusters].reset_index().values.tolist()]
        fig_centers = plot_lines_grid(
            df=model.df_cluster_centers[valid_clusters],
            subplot_titles=titles, return_p=True, h_each=300,
            legend=False, yaxes_visible=False, xaxes_visible=False, show_p=False
        )
        figs.append(html.Div(dcc.Graph(id='fig-centers', figure=fig_centers)))
    else:
        # plot clusters
        for cluster in valid_clusters:
            title = f"Cluster {cluster} (n={model.cluster_len_dict[cluster]}, score={model.cluster_quality_dict[cluster]})"
            plot_cols = model.cluster_metrics_dict[cluster]
            fig_cluster = plot_lines(
                df=model.df, cols=plot_cols, title=title, return_p=True, show_p=False,
                slider=False
            )
            figs.append(html.Div(dcc.Graph(id=f'fig-{cluster}', figure=fig_cluster)))

    states_previous = states_current

    return figs

