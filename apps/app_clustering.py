# -*- coding: utf-8 -*-

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

#DEFAULT_OPTS = 'k=20'
#DEFAULT_CHARTS_REGEX = 'system.*|apps.*|users.*|groups.*'
#DEFAULT_CHARTS_REGEX = '.*'
DEFAULT_OPTS = 'k=8'
DEFAULT_CHARTS_REGEX = 'system.*'

main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='cl-btn-run', n_clicks=0),
    ]
))
inputs_host = dbc.FormGroup(
    [
        dbc.Label('host', id='cl-label-host', html_for='cl-input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='cl-label-host')
    ]
)
inputs_charts_regex = dbc.FormGroup(
    [
        dbc.Label('charts regex', id='cl-label-charts-regex', html_for='cl-input-charts-regex', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-charts-regex', value=DEFAULT_CHARTS_REGEX, type='text', placeholder='system.*'),
        dbc.Tooltip('Regex for charts to pull.', target='cl-label-charts-regex')
    ]
)
inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='cl-label-after', html_for='cl-input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-after', value=-1800, type='number', placeholder=-1800),
        dbc.Tooltip('"after" as per netdata rest api.', target='cl-label-after')
    ]
)
inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='cl-label-before', html_for='cl-input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='cl-label-before')
    ]
)
inputs_opts = dbc.FormGroup(
    [
        dbc.Label('options', id='cl-label-opts', html_for='cl-input-opts', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cl-input-opts', value=DEFAULT_OPTS, type='text', placeholder=DEFAULT_OPTS),
        dbc.Tooltip('list of key values to pass to underlying code.', target='cl-label-opts')
    ]
)
inputs = dbc.Row(
    [
        dbc.Col(inputs_host, width=3),
        dbc.Col(inputs_charts_regex, width=2),
        dbc.Col(inputs_after, width=2),
        dbc.Col(inputs_before, width=2),
        dbc.Col(inputs_opts, width=2),
    ], style={'margin': '0px', 'padding': '0px'}
)
tabs = dbc.Tabs(
    [
        dbc.Tab(label='Cluster Centers', id='cl-id-tab-centers', tab_id='cl-tab-centers'),
        dbc.Tab(label='Cluster Details', id='cl-id-tab-details', tab_id='cl-tab-details'),
    ], id='cl-tabs', active_tab='cl-tab-centers', style={'margin': '12px', 'padding': '2px'}
)
layout = html.Div(
    [
        logo,
        main_menu,
        inputs,
        tabs,
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
def run(n_clicks, tab, host, charts_regex, after, before, opts='', k=20):

    # define some global variables and state change helpers
    global states_previous, states_current, inputs_previous, inputs_current
    global return_error
    global model, valid_clusters
    ctx = dash.callback_context
    inputs_current, states_current = ctx.inputs, ctx.states
    was_button_clicked, has_state_changed, is_initial_run = False, False, True
    if 'states_previous' in globals():
        if set(states_previous.values()) != set(states_current.values()):
            has_state_changed = True
        is_initial_run = False
    if 'inputs_previous' in globals():
        if inputs_current['cl-btn-run.n_clicks'] > inputs_previous['cl-btn-run.n_clicks']:
            was_button_clicked = True
    recalculate = True if was_button_clicked or is_initial_run or has_state_changed else False

    opts = process_opts(opts)
    k = int(opts.get('k', k))

    figs = []

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cl-fig-changepoint', figure=empty_fig)))
        return figs

    # only do expensive work if needed
    if recalculate:

        model = Clusterer([host], charts_regex=charts_regex, after=after, before=before, n_clusters=k)
        model.run_all()
        valid_clusters = model.df_cluster_meta[model.df_cluster_meta['valid'] == 1].index
        if len(valid_clusters) == 0:
            return_error = True
        else:
            return_error = False

    if return_error:
        figs.append(html.Div(dcc.Graph(id='cl-fig-changepoint', figure=make_empty_fig('No clusters found!'))))
        return figs

    if tab == 'cl-tab-centers':

        titles = [f'{int(x[0])} - n={int(x[1])}, qs={x[2]}' for x in
                  model.df_cluster_meta.loc[valid_clusters].reset_index().values.tolist()]
        fig_centers = plot_lines_grid(
            df=model.df_cluster_centers[valid_clusters],
            subplot_titles=titles, h_each=300,
            legend=False, yaxes_visible=False, xaxes_visible=False
        )
        figs.append(html.Div(dcc.Graph(id='cl-fig-centers', figure=fig_centers)))

    else:

        for cluster in valid_clusters:

            title = f"Cluster {cluster} (n={model.cluster_len_dict[cluster]}, score={model.cluster_quality_dict[cluster]})"
            plot_cols = model.cluster_metrics_dict[cluster]
            fig_cluster = plot_lines(
                df=model.df, cols=plot_cols, title=title, slider=False
            )
            figs.append(html.Div(dcc.Graph(id=f'fig-{cluster}', figure=fig_cluster)))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs

