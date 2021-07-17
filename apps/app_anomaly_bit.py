# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from netdata_pandas.data import get_data
from datetime import datetime, timedelta

from app import app
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_metrics, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs, make_inputs_netdata_url, parse_netdata_url
)
from apps.core.utils.utils import process_opts
from apps.core.plots.lines import plot_lines, plot_lines_grid
from apps.core.plots.scatter import plot_scatters
from apps.core.plots.hists import plot_hists
from apps.core.data.core import normalize_df, smooth_df
from apps.help.popup_metrics_explorer import help

# defaults
app_prefix = 'ab'
DEFAULT_OPTS = 'smooth_n=5,max_points=1000'
DEFAULT_METRICS = 'system.*'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=15), '%Y-%m-%dT%H:%M')
DEFAULT_BEFORE = datetime.strftime(datetime.utcnow() - timedelta(minutes=0), '%Y-%m-%dT%H:%M')

# inputs
main_menu = make_main_menu(app_prefix)
inputs_host = make_inputs_host(app_prefix)
inputs_metrics = make_inputs_metrics(app_prefix, DEFAULT_METRICS)
inputs_after = make_inputs_after(app_prefix, DEFAULT_AFTER)
inputs_before = make_inputs_before(app_prefix, DEFAULT_BEFORE)
inputs_opts = make_inputs_opts(app_prefix, DEFAULT_OPTS)
inputs_netdata_url = make_inputs_netdata_url(app_prefix)
inputs = make_inputs([(inputs_host, 6), (inputs_after, 3), (inputs_before, 3), (inputs_metrics, 6), (inputs_opts, 6), (inputs_netdata_url, 12)])

# layout
tabs = make_tabs(app_prefix, [('Lines', 'ts-plots')])
layout = html.Div([logo, main_menu, help, inputs, tabs, make_figs(f'{app_prefix}-figs')], style=DEFAULT_STYLE)


@app.callback(
    Output(f'{app_prefix}-figs', 'children'),
    Input(f'{app_prefix}-btn-run', 'n_clicks'),
    Input(f'{app_prefix}-tabs', 'active_tab'),
    State(f'{app_prefix}-input-host', 'value'),
    State(f'{app_prefix}-input-metrics', 'value'),
    State(f'{app_prefix}-input-after', 'value'),
    State(f'{app_prefix}-input-before', 'value'),
    State(f'{app_prefix}-input-opts', 'value'),
    State(f'{app_prefix}-input-netdata-url', 'value'),
)
def run(n_clicks, tab, host, metrics, after, before, opts='', netdata_url='',
        smooth_n='0', n_cols='3', h='1200', w='1200', diff='False', lw=1, legend='True', max_points=1000):
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
        if inputs_current[f'{app_prefix}-btn-run.n_clicks'] > inputs_previous[f'{app_prefix}-btn-run.n_clicks']:
            was_button_clicked = True
    recalculate = True if was_button_clicked or is_initial_run or has_state_changed else False

    figs = []

    opts = process_opts(opts)
    smooth_n = int(opts.get('smooth_n', smooth_n))
    n_cols = int(opts.get('n_cols', n_cols))
    h = int(opts.get('h', h))
    w = int(opts.get('w', w))
    lw = int(opts.get('lw', lw))
    legend = True if opts.get('legend', legend).lower() == 'true' else False
    diff = True if opts.get('diff', diff).lower() == 'true' else False
    max_points = int(opts.get('max_points', max_points))
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
    points = min(before-after, max_points)
    netdata_url_dict = parse_netdata_url(netdata_url)
    after = netdata_url_dict.get('after', after)
    before = netdata_url_dict.get('before', before)
    host = netdata_url_dict.get('host:port', host)

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig-empty', figure=make_empty_fig())))
        return figs

    if recalculate:

        metrics = metrics.split(',')
        charts = list(set([m.split('|')[0] for m in metrics]))
        df = get_data(hosts=[host], charts=charts, after=after, before=before, index_as_datetime=True, points=points)
        df_bit = get_data(hosts=[host], charts=charts, after=after, before=before, index_as_datetime=True, points=points, options='anomaly-bit')
        df = df[metrics]
        df_bit = df_bit[metrics] / 100
        dim_rank = df_bit.mean().sort_values(ascending=False)
        if smooth_n >= 1:
            df = smooth_df(df, smooth_n)
            df_bit = smooth_df(df_bit, smooth_n)
        if diff:
            df = df.diff()
            df_bit = df_bit.diff()

    if tab == f'{app_prefix}-tab-ts-plots':

        for col, ar in dim_rank.iteritems():
            df_plot = normalize_df(df[[col]]).join(df_bit[[col]].add_suffix('_bit'))
            fig = plot_lines(
                df_plot, title=f'{col} (AR={round(ar,4)}%)', h=600, lw=lw, visible_legendonly=False, hide_y_axis=True,
            )
            figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-{col}-fig-ts-plot', figure=fig)))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs
