# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from netdata_pandas.data import get_data
from datetime import datetime, timedelta

from app import app
from apps.core.data.core import smooth_df
from apps.core.metrics_model.core import preprocess_data, get_feature_importance, get_topn_model_score
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_generic, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs
)
from apps.core.utils.utils import process_opts
from apps.core.plots.lines import plot_lines_grid
from apps.help.popup_metrics_model import help

# defaults
app_prefix = 'mm'
DEFAULT_OPTS = 'top_n=10,n_estimators=100,max_depth=3,protocol=https,smooth_n=10,freq=1s,std_threshold=0.01'
DEFAULT_TARGET = 'system.cpu|user'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=5), '%Y-%m-%dT%H:%M')
DEFAULT_BEFORE = datetime.strftime(datetime.utcnow() - timedelta(minutes=0), '%Y-%m-%dT%H:%M')

# inputs
main_menu = make_main_menu(app_prefix)
inputs_host = make_inputs_host(app_prefix)
inputs_target = make_inputs_generic(
    prefix=app_prefix, suffix='target', input_type='text', default_value=DEFAULT_TARGET,
    tooltip_text='Metric you want to build a model for.', label_text='target metric'
)
inputs_after = make_inputs_after(app_prefix, DEFAULT_AFTER)
inputs_before = make_inputs_before(app_prefix, DEFAULT_BEFORE)
inputs_opts = make_inputs_opts(app_prefix, DEFAULT_OPTS)
inputs = make_inputs([(inputs_host, 6), (inputs_after, 3), (inputs_before, 3), (inputs_target, 3), (inputs_opts, 9)])

# layout
tabs = make_tabs(app_prefix, [('Results', 'results')])
layout = html.Div([logo, main_menu, help, inputs, tabs, make_figs(f'{app_prefix}-figs')], style=DEFAULT_STYLE)


@app.callback(
    Output(f'{app_prefix}-figs', 'children'),
    Input(f'{app_prefix}-btn-run', 'n_clicks'),
    Input(f'{app_prefix}-tabs', 'active_tab'),
    State(f'{app_prefix}-input-host', 'value'),
    State(f'{app_prefix}-input-target', 'value'),
    State(f'{app_prefix}-input-after', 'value'),
    State(f'{app_prefix}-input-before', 'value'),
    State(f'{app_prefix}-input-opts', 'value'),
)
def run(n_clicks, tab, host, target, after, before, opts='',
        top_n='10', protocol='https', freq='1s', smooth_n=10, n_estimators=100, max_depth=3,
        std_threshold=0.01, lw=1):

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
    top_n = int(opts.get('top_n', top_n))
    protocol = str(opts.get('protocol', protocol))
    freq = str(opts.get('freq', freq))
    smooth_n = int(opts.get('smooth_n', smooth_n))
    n_estimators = int(opts.get('n_estimators', n_estimators))
    max_depth = int(opts.get('max_depth', max_depth))
    lw = int(opts.get('lw', lw))
    std_threshold = float(opts.get('std_threshold', std_threshold))
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig-empty', figure=make_empty_fig())))
        return figs

    if recalculate:

        df = get_data(
            hosts=[host], charts_regex='.*', after=after,
            before=before, index_as_datetime=True, protocol=protocol,
            freq=freq
        )
        if smooth_n >= 1:
            df = smooth_df(df, smooth_n)

        # preprocess data
        df, X, y, colnames = preprocess_data(df, target, std_threshold)

        # get feature importance
        df_feature_importance = get_feature_importance(X, y, colnames, n_estimators, max_depth)
        top_n_features = list(df_feature_importance.head(top_n).index)

        # fit top n model score
        score = get_topn_model_score(df, y, top_n_features, n_estimators, max_depth)


    if tab == f'{app_prefix}-tab-results':

        fig = plot_lines_grid(
            df=pd.concat([pd.DataFrame(y, columns=['y'], index=df.index), df[top_n_features]],
                         axis=1),
            title=f'{target} - most predictive metrics by importance (r-square={score})',
            h_each=150,
            lw=lw,
            xaxes_visible=False,
            yaxes_visible=False,
            legend=False
        )
        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig', figure=fig)))

    else:

        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig', figure=make_empty_fig('Error!'))))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs

