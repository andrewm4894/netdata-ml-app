# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from netdata_pandas.data import get_data
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

from app import app
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_metrics, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs
)
from apps.core.utils.utils import process_opts
from apps.core.plots.lines import plot_lines_grid
from apps.help.popup_metrics_model import help

# defaults
app_prefix = 'mm'
DEFAULT_OPTS = 'top_n=10'
DEFAULT_METRICS = 'system.cpu|user'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=15), '%Y-%m-%dT%H:%M')
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
tabs = make_tabs(app_prefix, [('Results', 'results')])
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
)
def run(n_clicks, tab, host, metrics, after, before, opts='',
        top_n='10'):

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
    n_estimators = 250
    max_depth = 3
    std_threshold = 0.01
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig-empty', figure=make_empty_fig())))
        return figs

    if recalculate:

        metrics = metrics.split(',')
        df = get_data(hosts=[host], charts_regex='.*', after=after, before=before, index_as_datetime=True)
        print(df.shape)

        target = np.random.choice(df.columns, 1)[0]
        target_chart = target.split('|')[0]
        print(target)

        # make y
        y = (df[target].shift(-1) + df[target].shift(-2) + df[target].shift(-3)) / 3
        df = df.drop([target], axis=1)

        # drop cols from same chart
        cols_to_drop = [col for col in df.columns if col.startswith(f'{target_chart}|')]
        df = df.drop(cols_to_drop, axis=1)

        # drop useless cols
        df = df.drop(df.std()[df.std() < std_threshold].index.values, axis=1)
        print(df.shape)

        # work in diffs
        df = df.diff()

        # make x
        lags_n = 5
        colnames = [f'{col}_lag{n}' for n in [n for n in range(lags_n + 1)] for col in df.columns]
        df = pd.concat([df.shift(n) for n in range(lags_n + 1)], axis=1).dropna()
        df.columns = colnames
        df = df.join(y).dropna()
        y = df[target].values
        del df[target]
        X = df.values

        regr = RandomForestRegressor(max_depth=max_depth, n_estimators=n_estimators)
        regr.fit(X, y)

        # print r-square
        score = round(regr.score(X, y), 2)
        print(target)
        print(f'score={score}')

        df_feature_imp = pd.DataFrame.from_dict(
            {x[0]: x[1] for x in (zip(colnames, regr.feature_importances_))}, orient='index',
            columns=['importance']
        )
        df_feature_imp = df_feature_imp.sort_values('importance', ascending=False)
        print(df_feature_imp.head(10))

        # refit using top n features
        regr = RandomForestRegressor(max_depth=2, random_state=0, n_estimators=100)
        X = df[list(df_feature_imp.head(top_n).index)].values
        regr.fit(X, y)
        score = round(regr.score(X, y), 2)
        print(f'score={score}')

    if tab == f'{app_prefix}-tab-results':

        fig = plot_lines_grid(
            df=pd.concat([pd.DataFrame(y, columns=['y'], index=df.index), df[list(df_feature_imp.head(top_n).index)]],
                         axis=1),
            title=f'{target} - most predictive metrics by importance (r-square={score})',
            h_each=150,
            lw=2,
            xaxes_visible=False,
            yaxes_visible=False,
        )
        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig', figure=fig)))

    else:

        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig', figure=make_empty_fig('Error!'))))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs

