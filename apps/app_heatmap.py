# -*- coding: utf-8 -*-
import time

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px
from netdata_pandas.data import get_data
from sklearn.cluster import AgglomerativeClustering
from datetime import datetime, timedelta

from app import app
from apps.core.data.core import app_get_data
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_charts_regex, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs, make_inputs_netdata_url, parse_netdata_url
)
from apps.core.utils.utils import process_opts, log_inputs
from apps.help.popup_heatmap import help

# defaults
app_prefix = 'hm'
DEFAULT_OPTS = 'freq=30s,w=1200'
#DEFAULT_CHARTS_REGEX = 'system.*|apps.*|users.*|groups.*'
DEFAULT_CHARTS_REGEX = 'system.*'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=30), '%Y-%m-%dT%H:%M')
DEFAULT_BEFORE = datetime.strftime(datetime.utcnow() - timedelta(minutes=0), '%Y-%m-%dT%H:%M')

# inputs
main_menu = make_main_menu(app_prefix)
inputs_host = make_inputs_host(app_prefix)
inputs_charts_regex = make_inputs_charts_regex(app_prefix, DEFAULT_CHARTS_REGEX)
inputs_after = make_inputs_after(app_prefix, DEFAULT_AFTER)
inputs_before = make_inputs_before(app_prefix, DEFAULT_BEFORE)
inputs_opts = make_inputs_opts(app_prefix, DEFAULT_OPTS)
inputs_netdata_url = make_inputs_netdata_url(app_prefix)
inputs = make_inputs([(inputs_host, 6), (inputs_after, 3), (inputs_before, 3), (inputs_charts_regex, 6), (inputs_opts, 6), (inputs_netdata_url, 12)])

# layout
tabs = make_tabs(app_prefix, [('Clustered Heatmap', 'heatmap-clustered')])
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
    State(f'{app_prefix}-input-netdata-url', 'value'),
)
def run(n_clicks, tab, host, charts_regex, after, before, opts='', netdata_url='', freq='10s', w='1200', thold=None,
        norm='True', max_points=1000, options=''):

    time_start = time.time()

    figs = []

    opts = process_opts(opts)
    freq = opts.get('freq', freq)
    w = int(opts.get('w', w))
    thold = opts.get('thold', thold)
    options = opts.get('options', options)
    norm = bool(opts.get('norm', norm))
    max_points = int(opts.get('max_points', max_points))
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
    points = min(before - after, max_points)
    netdata_url_dict = parse_netdata_url(netdata_url)
    after = netdata_url_dict.get('after', after)
    before = netdata_url_dict.get('before', before)
    host = netdata_url_dict.get('host:port', host)

    log_inputs(app, host, after, before, points, charts_regex=charts_regex)

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cp-fig', figure=make_empty_fig())))
        return figs

    else:

        # get data
        df = app_get_data(app, host=host, charts_regex=charts_regex, after=after, before=before, points=points,
                          options=options)
        # lets resample to a specific frequency
        df = df.resample(freq).mean()
        # apply thold if specified
        if thold:
            df = pd.DataFrame(
                data=np.where(df >= float(thold), 1, 0),
                columns=df.columns,
                index=df.index
            )
        # lets min-max normalize our data so metrics can be compared on a heatmap
        if norm:
            df = (df - df.min()) / (df.max() - df.min())
        # drop na cols
        df = df.dropna(how='all', axis=1)
        # lets do some clustering to sort similar cols
        clustering = AgglomerativeClustering(
            n_clusters=int(round(len(df.columns) * 0.2, 0))
        ).fit(df.fillna(0).transpose().values)
        # get order of cols from the cluster labels
        cols_sorted = pd.DataFrame(
            zip(df.columns, clustering.labels_),
            columns=['metric', 'cluster']
        ).sort_values('cluster')['metric'].values.tolist()
        # re-order cols
        df = df[cols_sorted]

        fig = px.imshow(df.transpose(), color_continuous_scale='Greens')
        fig.update_layout(
            autosize=False,
            width=w,
            height=len(df.columns)*20)
        figs.append(html.Div(dcc.Graph(id='hm-fig', figure=fig)))

    app.logger.debug(f'time to finish = {time.time() - time_start}')

    return figs

