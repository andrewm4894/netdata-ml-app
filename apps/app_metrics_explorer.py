# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from netdata_pandas.data import get_data
from datetime import datetime, timedelta

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, make_empty_fig
from .utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_metrics, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs
)
from .utils.utils import process_opts
from .plots.lines import plot_lines, plot_lines_grid
from .plots.scatter import plot_scatters
from .plots.hists import plot_hists
from .data.core import normalize_df, smooth_df
from .help_popup.metrics_explorer import help, toggle_help

# defaults
app_prefix = 'me'
DEFAULT_OPTS = 'smooth_n=5'
#DEFAULT_METRICS = 'system.cpu|user,system.cpu|system,system.load|load1'
DEFAULT_METRICS = 'system.cpu|user,system.cpu|system,system.ram|free,system.net|sent,system.load|load1,system.ip|sent,system.ip|received,system.intr|interrupts,system.processes|running,system.forks|started,system.io|out'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=30), '%Y-%m-%dT%H:%M')
DEFAULT_BEFORE = datetime.strftime(datetime.utcnow() - timedelta(minutes=0), '%Y-%m-%dT%H:%M')

# inputs
main_menu = make_main_menu(app_prefix)
inputs_host = make_inputs_host(app_prefix)
inputs_metrics = make_inputs_metrics(app_prefix, DEFAULT_METRICS)
inputs_after = make_inputs_after(app_prefix, DEFAULT_AFTER)
inputs_before = make_inputs_before(app_prefix, DEFAULT_BEFORE)
inputs_opts = make_inputs_opts(app_prefix, DEFAULT_OPTS)
inputs = make_inputs([(inputs_host, 6), (inputs_after, 3), (inputs_before, 3), (inputs_metrics, 6), (inputs_opts, 6)])

# layout
tabs = make_tabs(app_prefix, [('Lines', 'ts-plots'), ('Scatter', 'scatter-plots'), ('Histograms', 'hist-plots')])
layout = html.Div([logo, main_menu, help, inputs, tabs, make_figs(f'{app_prefix}-figs')], style=DEFAULT_STYLE)


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
def run(n_clicks, tab, host, metrics, after, before, opts='',
        smooth_n='0', n_cols='3', h='1200', w='1200', diff='False'):

    # define some global variables and state change helpers
    global states_previous, states_current, inputs_previous, inputs_current
    global df
    ctx = dash.callback_context
    inputs_current, states_current = ctx.inputs, ctx.states
    was_button_clicked, has_state_changed, is_initial_run = False, False, True
    if 'states_previous' in globals():
        if set(states_previous.values()) != set(states_current.values()):
            has_state_changed = True
        is_initial_run = False
    if 'inputs_previous' in globals():
        if inputs_current['me-btn-run.n_clicks'] > inputs_previous['me-btn-run.n_clicks']:
            was_button_clicked = True
    recalculate = True if was_button_clicked or is_initial_run or has_state_changed else False

    figs = []

    opts = process_opts(opts)
    smooth_n = int(opts.get('smooth_n', smooth_n))
    n_cols = int(opts.get('n_cols', n_cols))
    h = int(opts.get('h', h))
    w = int(opts.get('w', w))
    diff = True if opts.get('diff', diff).lower() == 'true' else False
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='me-fig-empty', figure=make_empty_fig())))
        return figs

    if recalculate:

        metrics = metrics.split(',')
        charts = list(set([m.split('|')[0] for m in metrics]))
        df = get_data(hosts=[host], charts=charts, after=after, before=before, index_as_datetime=True)
        df = df[metrics]
        if smooth_n >= 1:
            df = smooth_df(df, smooth_n)
        if diff:
            df = df.diff()

    if tab == 'me-tab-ts-plots':

        fig = plot_lines(
            normalize_df(df), h=600, lw=1, visible_legendonly=False, hide_y_axis=True
        )
        figs.append(html.Div(dcc.Graph(id='me-fig-ts-plot', figure=fig)))

        fig = plot_lines_grid(
            df, h=max(300, 75*len(df.columns)), xaxes_visible=False, legend=True, yaxes_visible=False, subplot_titles=[''],

        )
        figs.append(html.Div(dcc.Graph(id='me-fig-ts-plot-grid', figure=fig)))

    elif tab == 'me-tab-scatter-plots':

        fig = plot_scatters(
            df, n_cols=n_cols, w=w, h=600*len(df.columns)
        )
        figs.append(html.Div(dcc.Graph(id='me-fig-scatter-plot', figure=fig)))

    elif tab == 'me-tab-hist-plots':

        fig = plot_hists(
            df, shared_yaxes=False, n_cols=n_cols, w=w, h=1200,
        )
        figs.append(html.Div(dcc.Graph(id='me-fig-hist-plot', figure=fig)))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs

