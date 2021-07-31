# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from netdata_pandas.data import get_data
from datetime import datetime, timedelta
from scipy.spatial.distance import cdist
import pandas as pd

from app import app
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_metrics, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs, make_inputs_netdata_url, parse_netdata_url, make_inputs_generic
)
from apps.core.utils.utils import process_opts
from apps.core.plots.lines import plot_lines, plot_lines_grid
from apps.core.plots.scatter import plot_scatters
from apps.core.plots.hists import plot_hists
from apps.core.data.core import normalize_df, smooth_df
from apps.help.popup_metrics_similarity import help

# defaults
app_prefix = 'ms'
DEFAULT_OPTS = 'smooth_n=5,max_points=1000,top_n=25,distance=cosine'
DEFAULT_TARGET = 'system.cpu|user'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=15), '%Y-%m-%dT%H:%M')
DEFAULT_BEFORE = datetime.strftime(datetime.utcnow() - timedelta(minutes=0), '%Y-%m-%dT%H:%M')

# inputs
main_menu = make_main_menu(app_prefix)
inputs_host = make_inputs_host(app_prefix)
inputs_target = make_inputs_generic(
    prefix=app_prefix, suffix='target', input_type='text', default_value=DEFAULT_TARGET,
    tooltip_text='Metric you want to find similar metrics to.', label_text='target metric'
)
inputs_after = make_inputs_after(app_prefix, DEFAULT_AFTER)
inputs_before = make_inputs_before(app_prefix, DEFAULT_BEFORE)
inputs_opts = make_inputs_opts(app_prefix, DEFAULT_OPTS)
inputs_netdata_url = make_inputs_netdata_url(app_prefix)
inputs = make_inputs([(inputs_host, 6), (inputs_after, 3), (inputs_before, 3), (inputs_target, 6), (inputs_opts, 6), (inputs_netdata_url, 12)])

# layout
layout = html.Div([logo, main_menu, help, inputs, make_figs(f'{app_prefix}-figs')], style=DEFAULT_STYLE)


@app.callback(
    Output(f'{app_prefix}-figs', 'children'),
    Input(f'{app_prefix}-btn-run', 'n_clicks'),
    State(f'{app_prefix}-input-host', 'value'),
    State(f'{app_prefix}-input-after', 'value'),
    State(f'{app_prefix}-input-before', 'value'),
    State(f'{app_prefix}-input-target', 'value'),
    State(f'{app_prefix}-input-opts', 'value'),
    State(f'{app_prefix}-input-netdata-url', 'value'),
)
def run(n_clicks, host, after, before, target, opts='', netdata_url='',
        smooth_n='0', top_n='25', distance='cosine', h_each='200', diff='False',
        lw=1, legend='False', max_points=1000):
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
    h_each = int(opts.get('h_each', h_each))
    top_n = int(opts.get('top_n', top_n))
    distance = opts.get('distance', distance)
    legend = True if opts.get('legend', legend).lower() == 'true' else False
    diff = True if opts.get('diff', diff).lower() == 'true' else False
    max_points = int(opts.get('max_points', max_points))
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
    points = min(before-after, max_points)
    netdata_url_dict = parse_netdata_url(netdata_url)
    after = netdata_url_dict.get('after', after)
    before = netdata_url_dict.get('before', before)
    host = netdata_url_dict.get('host', host)

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig-empty', figure=make_empty_fig())))
        return figs

    if recalculate:

        df = get_data(hosts=[host], charts=['all'], after=after, before=before, index_as_datetime=True, points=points)
        df_raw = df.copy()
        df = (df - df.min()) / (df.max() - df.min())
        df = df.fillna(0)
        if smooth_n >= 1:
            df = smooth_df(df, smooth_n)
        if diff:
            df = df.diff()

    df_dist = pd.DataFrame(
        data=zip(df.columns, cdist(df[[target]].fillna(0).transpose(), df.fillna(0).transpose(), distance)[0]),
        columns=['metric', 'distance']
    )
    if distance == 'cosine':
        df_dist['rank'] = (1 - df_dist['distance']).rank(ascending=False)
    else:
        df_dist['rank'] = df_dist['distance'].rank()
    df_dist = df_dist.sort_values('rank')

    plot_cols = df_dist.head(top_n)['metric'].values.tolist()
    fig = plot_lines_grid(
        df_raw,
        plot_cols,
        h_each=h_each, legend=legend, yaxes_visible=False, xaxes_visible=False
    )
    figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig-ts-plot', figure=fig)))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs
