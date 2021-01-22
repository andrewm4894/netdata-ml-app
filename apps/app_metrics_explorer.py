# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from netdata_pandas.data import get_data

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, empty_fig
from .utils.utils import process_opts
from .plots.lines import plot_lines, plot_lines_grid
from .data.core import normalize_df, smooth_df

DEFAULT_ME_OPTS = 'smooth_n=5'

me_main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='me-btn-run', n_clicks=0),
    ]
))
me_inputs_host = dbc.FormGroup(
    [
        dbc.Label('host', id='me-label-host', html_for='me-input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='me-input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='me-label-host')
    ]
)
me_inputs_metrics = dbc.FormGroup(
    [
        dbc.Label('metrics', id='me-label-metrics', html_for='me-input-metrics', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='me-input-metrics', value='system.cpu|user,system.cpu|system,system.ram|free,system.net|sent', type='text', placeholder='system.cpu|user,system.cpu|system,system.ram|free,system.net|sent'),
        dbc.Tooltip('Metrics to explore.', target='me-label-metrics')
    ]
)
me_inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='me-label-after', html_for='me-input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='me-input-after', value=-1800, type='number', placeholder=-1800),
        dbc.Tooltip('"after" as per netdata rest api.', target='me-label-after')
    ]
)
me_inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='me-label-before', html_for='me-input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='me-input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='me-label-before')
    ]
)
me_inputs_opts = dbc.FormGroup(
    [
        dbc.Label('options', id='me-label-opts', html_for='me-input-opts', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='me-input-opts', value=DEFAULT_ME_OPTS, type='text', placeholder=DEFAULT_ME_OPTS),
        dbc.Tooltip('list of key values to pass to underlying code.', target='me-label-opts')
    ]
)
me_inputs = dbc.Row(
    [
        dbc.Col(me_inputs_host, width=3),
        dbc.Col(me_inputs_metrics, width=3),
        dbc.Col(me_inputs_after, width=2),
        dbc.Col(me_inputs_before, width=2),
        dbc.Col(me_inputs_opts, width=2),
    ], style={'margin': '0px', 'padding': '0px'}
)
me_tabs = dbc.Tabs(
    [
        dbc.Tab(label='Time Series Plots', tab_id='me-tab-ts-plots'),
    ], id='me-tabs', active_tab='me-tab-ts-plots', style={'margin': '12px', 'padding': '2px'}
)
layout = html.Div(
    [
        logo,
        me_main_menu,
        me_inputs,
        me_tabs,
        dbc.Spinner(children=[html.Div(children=html.Div(id='me-figs'))]),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('me-figs', 'children'),
    Input('me-btn-run', 'n_clicks'),
    Input('me-tabs', 'active_tab'),
    State('me-input-host', 'value'),
    State('me-input-metrics', 'value'),
    State('me-input-after', 'value'),
    State('me-input-before', 'value'),
    State('me-input-opts', 'value'),
)
def cp_run(n_clicks, tab, host, metrics, after, before, opts='', smooth_n='0'):

    figs = []

    opts = process_opts(opts)
    smooth_n = int(opts.get('smooth_n', smooth_n))

    if n_clicks == 0:

        figs.append(html.Div(dcc.Graph(id='cp-fig-changepoint', figure=empty_fig)))

    else:

        metrics = metrics.split(',')
        charts = list(set([m.split('|')[0] for m in metrics]))
        df = get_data(hosts=[host], charts=charts, after=after, before=before, index_as_datetime=True)
        df = df[metrics]

        if smooth_n >= 1:
            df = smooth_df(df, smooth_n)

        if tab == 'me-tab-ts-plots':

            fig = plot_lines(
                normalize_df(df), title=f'Normalized Time Series Plot', return_p=True,
                show_p=False, h=600, lw=1
            )
            figs.append(html.Div(dcc.Graph(id='me-fig-ts-plot', figure=fig)))

            fig = plot_lines_grid(
                df, title=f'Sparkline Plots', return_p=True, show_p=False,
                xaxes_visible=False, legend=False, yaxes_visible=False
            )
            figs.append(html.Div(dcc.Graph(id='me-fig-ts-plot-grid', figure=fig)))

    return figs

