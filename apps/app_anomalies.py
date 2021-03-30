# -*- coding: utf-8 -*-

from datetime import timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from netdata_pandas.data import get_data
from pyod.models.hbos import HBOS
from pyod.models.pca import PCA
from sklearn.cluster import AgglomerativeClustering

from app import app
from .plots.lines import plot_lines, plot_lines_grid
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, make_empty_fig
from .utils.utils import process_opts
from .utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_charts_regex, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs
)
from .utils.utils import process_opts, get_reference_timedelta, get_ref_windows
from .anomalies.core import make_features
from .help_popup.anomalies import help, toggle_help

# defaults
app_prefix = 'ad'
DEFAULT_OPTS = 'train=4h,freq=10s'
DEFAULT_CHARTS_REGEX = 'system.*'
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
tabs = make_tabs(
    app_prefix,
    [
        ('Anomaly Flags', 'anomaly-preds'),
        ('Anomaly Probabilities', 'anomaly-probs'),
        ('Anomaly Heatmaps', 'anomaly-heatmap'),
        ('Charts', 'charts'),
    ],
)
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
def run(n_clicks, tab, host, charts_regex, after, before, opts, train='1h', freq='15s', lags_n=3, diffs_n=1,
        smooth_n=3, contamination=0.01):

    # define some global variables and state change helpers
    global states_previous, states_current, inputs_previous, inputs_current
    global df, df_train, df_preds, df_probs, charts
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
    train = opts.get('train', train)
    freq = opts.get('freq', freq)
    contamination = opts.get('contamination', contamination)

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cor-fig', figure=make_empty_fig())))
        return figs

    if recalculate:

        train_timedelta = get_reference_timedelta(train)
        after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
        before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
        df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
        train_before, train_after = get_ref_windows(train_timedelta, df)
        df_train = get_data(hosts=[host], charts_regex=charts_regex, after=train_after, before=train_before, index_as_datetime=True)

        if freq:
            df = df.resample(freq).mean()
            df_train = df_train.resample(freq).mean()

        # make features
        colnames_train, arr_train = make_features(df_train.values, list(df_train.columns), lags_n, diffs_n, smooth_n)
        colnames, arr = make_features(df.values, list(df.columns), lags_n, diffs_n, smooth_n)
        df_features = pd.DataFrame(arr, columns=colnames).ffill().bfill()
        df_features_train = pd.DataFrame(arr_train, columns=colnames_train).ffill().bfill()

        # build models and get anomaly scores
        charts = list(set([col.split('|')[0] for col in df.columns]))
        preds, probs = {}, {}

        for chart in charts:

            chart_cols = [col for col in df_features.columns if col.startswith(f'{chart}|')]
            model = PCA(contamination=contamination)
            X_train = df_features_train[chart_cols].values
            X = df_features[chart_cols].values
            try:
                model.fit(X_train)
                preds[chart] = model.predict(X)
                probs[chart] = model.predict_proba(X)[:, 1].tolist()
            except:
                model = HBOS(contamination=contamination)
                model.fit(X_train)
                preds[chart] = model.predict(X)
                probs[chart] = model.predict_proba(X)[:, 1].tolist()

        df_preds = pd.DataFrame.from_dict(preds, orient='columns')
        df_probs = pd.DataFrame.from_dict(probs, orient='columns')
        len_preds = len(df_preds)
        df_preds['time'] = df.tail(len_preds).index
        df_preds = df_preds.set_index('time')
        df_probs['time'] = df.tail(len_preds).index
        df_probs = df_probs.set_index('time')

        df_probs['average_probability'] = df_probs.mean(axis=1)
        df_preds['anomaly_count'] = df_preds.sum(axis=1)

    if tab == f'{app_prefix}-tab-anomaly-probs':

        fig = plot_lines(df_probs, h=600, show_p=False, return_p=True)
        figs.append(html.Div(dcc.Graph(id='ad-fig-lines', figure=fig)))

        fig = plot_lines_grid(
            df_probs, sorted(df_probs.columns), h=75*len(df_probs.columns), yaxes_visible=False, xaxes_visible=False,
            subplot_titles=['' for i in range(len(df_probs.columns))], show_p=False, return_p=True
        )
        figs.append(html.Div(dcc.Graph(id='ad-fig', figure=fig)))

    elif tab == f'{app_prefix}-tab-anomaly-preds':

        plot_cols = [c for c in df_preds.columns if c != 'anomaly_count']
        fig = plot_lines(df_preds, plot_cols, h=600, show_p=False, return_p=True, stacked=True, lw=0)
        figs.append(html.Div(dcc.Graph(id='ad-fig-lines', figure=fig)))

        fig = plot_lines_grid(
            df_preds, sorted(df_preds.columns), h=75*len(df_preds.columns), yaxes_visible=False, xaxes_visible=False,
            subplot_titles=['' for i in range(len(df_preds.columns))], show_p=False, return_p=True
        )
        figs.append(html.Div(dcc.Graph(id='ad-fig', figure=fig)))

    elif tab == f'{app_prefix}-tab-charts':

        i = 0
        models = list(df_preds.sum().sort_values(ascending=False).index)
        models = [m for m in models if m != 'anomaly_count']
        for chart in models:

            anomaly_rate = round(df_preds[chart].mean() * 100, 2)

            chart_cols = [col for col in df.columns if col.startswith(f'{chart}|')]
            shade_regions = [(i, i + timedelta(seconds=10), 'red') for i in df_preds[df_preds[chart] == 1].index]
            title = f'{chart} - Raw Data ({anomaly_rate}% anomalous)'
            fig = plot_lines(
                df, chart_cols, h=500, show_p=False, return_p=True, title=title, shade_regions=shade_regions
            )
            fig.update_layout(showlegend=False)
            figs.append(html.Div(dcc.Graph(id=f'ad-fig-chart-{i}', figure=fig)))
            title = f'{chart} - Anomaly Probability'
            fig = plot_lines(
                df_probs, [chart], h=500, show_p=False, return_p=True, title=title
            )
            figs.append(html.Div(dcc.Graph(id=f'ad-fig-chart-as-{i}', figure=fig)))
            i += 1

    elif tab == f'{app_prefix}-tab-anomaly-heatmap':

        n_clusters = int(round(len(df_probs.columns) * 0.2, 0))
        columns = ['chart', 'cluster']
        colors = 'Greens'

        clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(df_preds.fillna(0).transpose().values)
        cols_labels = zip(df_preds.columns, clustering.labels_)
        cols_sorted = pd.DataFrame(cols_labels, columns=columns).sort_values('cluster')['chart'].values.tolist()
        df_preds = df_preds[cols_sorted]
        plot_cols = [col for col in cols_sorted if col != 'anomaly_count']
        fig = px.imshow(df_preds[plot_cols].transpose(), color_continuous_scale=colors)
        fig.update_layout(autosize=False, width=1400, height=len(df_preds.columns) * 40)
        figs.append(html.Div(dcc.Graph(id='ad-fig-heatmap-preds', figure=fig)))

        clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(df_probs.fillna(0).transpose().values)
        cols_labels = zip(df_probs.columns, clustering.labels_)
        cols_sorted = pd.DataFrame(cols_labels, columns=columns).sort_values('cluster')['chart'].values.tolist()
        df_probs = df_probs[cols_sorted]
        fig = px.imshow(df_probs.transpose(), color_continuous_scale=colors)
        fig.update_layout(autosize=False, width=1400, height=len(df_probs.columns) * 40)
        figs.append(html.Div(dcc.Graph(id='ad-fig-heatmap-probs', figure=fig)))

    else:

        figs.append(html.Div(dcc.Graph(id='ad-fig', figure=make_empty_fig('Error!'))))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs
