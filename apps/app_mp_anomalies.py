# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from netdata_pandas.data import get_data
import stumpy

from app import app
from .plots.lines import plot_lines_grid
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, make_empty_fig
from .utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_charts_regex, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs
)
from .utils.utils import process_opts
from .help_popup.mp_anomalies import help, toggle_help

# defaults
app_prefix = 'mp'
DEFAULT_OPTS = 'm=30,freq=15s,n_results=100'
DEFAULT_CHARTS_REGEX = 'system.*|apps.*|users.*'
#DEFAULT_CHARTS_REGEX = '.*'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=60), '%Y-%m-%dT%H:%M')
DEFAULT_BEFORE = datetime.strftime(datetime.utcnow() - timedelta(minutes=0), '%Y-%m-%dT%H:%M')

# inputs
main_menu = make_main_menu(app_prefix)
inputs_host = make_inputs_host(app_prefix)
inputs_charts_regex = make_inputs_charts_regex(app_prefix, DEFAULT_CHARTS_REGEX)
inputs_after = make_inputs_after(app_prefix, DEFAULT_AFTER)
inputs_before = make_inputs_before(app_prefix, DEFAULT_BEFORE)
inputs_opts = make_inputs_opts(app_prefix, DEFAULT_OPTS)
inputs = make_inputs([(inputs_host, 6), (inputs_after, 3), (inputs_before, 3), (inputs_charts_regex, 6), (inputs_opts, 6)])

# layout
tabs = make_tabs(app_prefix, [('Anomalies', 'anomalies')])
layout = html.Div([logo, main_menu, help, inputs, tabs, make_figs(f'{app_prefix}-figs')], style=DEFAULT_STYLE)


@app.callback(
    Output(f'{app_prefix}-figs', 'children'),
    Input(f'{app_prefix}-btn-run', 'n_clicks'),
    Input(f'{app_prefix}-tabs', 'active_tab'),
    State(f'{app_prefix}-input-host', 'value'),
    State(f'{app_prefix}-input-charts-regex', 'value'),
    State(f'{app_prefix}-input-after', 'value'),
    State(f'{app_prefix}-input-before', 'value'),
    State(f'{app_prefix}-input-opts', 'value'),
)
def run(n_clicks, tab, host, charts_regex, after, before, opts, freq='15s', m=30, n_results=100):

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
    freq = opts.get('freq', freq)
    m = int(opts.get('m', m))
    n_results = int(opts.get('n_results', n_results))

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='mp-fig', figure=make_empty_fig())))
        return figs

    if recalculate:

        after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
        before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
        df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
        if freq:
            df = df.resample(freq).mean()

        # define some objects to store results in
        scores = {}
        mp_dists = {}

        # normalize the data prior to computing the mp so that the scores we use
        # are all somewhat comparable across metrics on different scales
        df = ((df - df.min()) / (df.max() - df.min()))
        df = df.dropna(how='all', axis=1)
        df = df.dropna(how='all', axis=0)

        # loop over each metric
        for col in df.columns:
            # get the mp
            x = df[col]
            mp = stumpy.stump(x, m=m, ignore_trivial=True, normalize=False)
            mp_dist = mp[:, 0]

            # score the mp based on distance between the 99.5th percentile and 80th percentile
            df_mp_dist = pd.DataFrame(mp_dist)
            score = df_mp_dist[0].quantile(0.995) - df_mp_dist[0].quantile(0.8)
            scores[col] = score

            # pad out the start of the mp_dist with nan's
            n_fill = len(df[col]) - len(mp_dist)
            filler = np.empty(n_fill)
            filler.fill(np.nan)
            mp_dist = np.concatenate((filler, mp_dist.astype(float)))

            # save the mp
            mp_dists[col] = mp_dist

        df_scores = pd.DataFrame.from_dict(scores, orient='index')
        df_scores.columns = ['score']
        df_scores = df_scores.replace([np.inf, -np.inf], np.nan).dropna()
        df_scores['rank'] = df_scores['score'].rank(ascending=False)
        df_scores = df_scores.sort_values('rank')

    if tab == f'{app_prefix}-tab-anomalies':

        for col in df_scores.sort_values('rank').head(n_results).index:

            score = round(df_scores.loc[col]['score'], 2)
            rank = int(df_scores.loc[col]['rank'])
            df_tmp = df[[col]]
            df_tmp['mp'] = mp_dists[col]

            fig = plot_lines_grid(df_tmp, title=f'{col} (rank={rank}, score={score})', subplot_titles='', legend=False)
            figs.append(html.Div(dcc.Graph(id='mp-fig-lines', figure=fig)))

    else:

        figs.append(html.Div(dcc.Graph(id='mp-fig', figure=make_empty_fig('Error!'))))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs
