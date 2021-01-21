# -*- coding: utf-8 -*-

import time
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, empty_fig, make_empty_fig
from .utils.utils import process_opts
from .clustering.core import Clusterer
from .plots.lines import plot_lines, plot_lines_grid

DEFAULT_CL_OPTS = 'k=20'

cl_main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='cl-btn-run', n_clicks=0),
    ]
))
cl_inputs_host = dbc.FormGroup(
    [
        dbc.Label('host', id='cl-label-host', html_for='cl-input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='cl-label-host')
    ]
)
cl_inputs_charts_regex = dbc.FormGroup(
    [
        dbc.Label('charts regex', id='cl-label-charts-regex', html_for='cl-input-charts-regex', style={'margin': '4px', 'padding': '0px'}),
        #dbc.Input(id='cl-input-charts-regex', value='system.*|apps.*|users.*|groups.*', type='text', placeholder='system.*'),
        dbc.Input(id='cl-input-charts-regex', value='.*', type='text', placeholder='system.*'),
        dbc.Tooltip('Regex for charts to pull.', target='cl-label-charts-regex')
    ]
)
cl_inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='cl-label-after', html_for='cl-input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-after', value=-1800, type='number', placeholder=-1800),
        dbc.Tooltip('"after" as per netdata rest api.', target='cl-label-after')
    ]
)
cl_inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='cl-label-before', html_for='cl-input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='cl-label-before')
    ]
)
cl_inputs_opts = dbc.FormGroup(
    [
        dbc.Label('options', id='cl-label-opts', html_for='cl-input-opts', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-opts', value=DEFAULT_CL_OPTS, type='text', placeholder=DEFAULT_CL_OPTS),
        dbc.Tooltip('list of key values to pass to underlying code.', target='cl-label-opts')
    ]
)
cl_inputs = dbc.Row(
    [
        dbc.Col(cl_inputs_host, width=3),
        dbc.Col(cl_inputs_charts_regex, width=2),
        dbc.Col(cl_inputs_after, width=2),
        dbc.Col(cl_inputs_before, width=2),
        dbc.Col(cl_inputs_opts, width=2),
    ], style={'margin': '0px', 'padding': '0px'}
)
cl_tabs = dbc.Tabs(
    [
        dbc.Tab(label='Cluster Centers', id='cl-id-tab-centers', tab_id='cl-tab-centers'),
        dbc.Tab(label='Cluster Details', id='cl-id-tab-details', tab_id='cl-tab-details'),
    ], id='cl-tabs', active_tab='cl-tab-centers', style={'margin': '12px', 'padding': '2px'}
)
layout = html.Div(
    [
        logo,
        cl_main_menu,
        cl_inputs,
        cl_tabs,
        dbc.Spinner(children=[html.Div(children=html.Div(id='cl-figs'))]),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('cl-figs', 'children'),
    Input('cl-btn-run', 'n_clicks'),
    Input('cl-tabs', 'active_tab'),
    State('cl-input-host', 'value'),
    State('cl-input-charts-regex', 'value'),
    State('cl-input-after', 'value'),
    State('cl-input-before', 'value'),
    State('cl-input-opts', 'value')
)
def cl_run(n_clicks, tab, host, charts_regex, after, before, opts='', k=20):

    time_start = time.time()

    def run_model(host, charts_regex, after, before, k):
        model = Clusterer([host], charts_regex=charts_regex, after=after, before=before, n_clusters=k)
        model.run_all()
        valid_clusters = model.df_cluster_meta[model.df_cluster_meta['valid'] == 1].index
        return model, valid_clusters

    opts = process_opts(opts)
    k = int(opts.get('k', k))

    cl_ctx = dash.callback_context

    global cl_states_previous
    global cl_states_current
    global cl_inputs_previous
    global cl_inputs_current
    global cl_model
    global cl_valid_clusters

    cl_states_current = cl_ctx.states
    cl_inputs_current = cl_ctx.inputs

    figs = []

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cl-fig-changepoint', figure=empty_fig)))
        return figs

    if 'cl_states_previous' in globals():

        if set(cl_states_previous.values()) != set(cl_states_current.values()):
            cl_model, cl_valid_clusters = run_model(host, charts_regex, after, before, k)
        elif cl_inputs_current['cl-btn-run.n_clicks'] != cl_inputs_previous['cl-btn-run.n_clicks']:
            cl_model, cl_valid_clusters = run_model(host, charts_regex, after, before, k)

    else:

        cl_model, cl_valid_clusters = run_model(host, charts_regex, after, before, k)

    if len(cl_valid_clusters) == 0:
        figs.append(html.Div(dcc.Graph(id='cl-fig-changepoint', figure=make_empty_fig('No clusters found!'))))
        return figs

    if tab == 'cl-tab-centers':

        titles = [f'{int(x[0])} - n={int(x[1])}, qs={x[2]}' for x in
                  cl_model.df_cluster_meta.loc[cl_valid_clusters].reset_index().values.tolist()]
        fig_centers = plot_lines_grid(
            df=cl_model.df_cluster_centers[cl_valid_clusters],
            subplot_titles=titles, return_p=True, h_each=300,
            legend=False, yaxes_visible=False, xaxes_visible=False, show_p=False
        )
        figs.append(html.Div(dcc.Graph(id='cl-fig-centers', figure=fig_centers)))

    else:

        for cluster in cl_valid_clusters:

            title = f"Cluster {cluster} (n={cl_model.cluster_len_dict[cluster]}, score={cl_model.cluster_quality_dict[cluster]})"
            plot_cols = cl_model.cluster_metrics_dict[cluster]
            fig_cluster = plot_lines(
                df=cl_model.df, cols=plot_cols, title=title, return_p=True, show_p=False,
                slider=False
            )
            figs.append(html.Div(dcc.Graph(id=f'fig-{cluster}', figure=fig_cluster)))

    cl_states_previous = cl_states_current
    cl_inputs_previous = cl_inputs_current

    time_end = time.time()
    time_taken = round(time_end - time_start, 2)
    print(f'time_taken={time_taken}')

    return figs

