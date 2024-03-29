# -*- coding: utf-8 -*-
import time

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from netdata_pandas.data import get_data
from datetime import datetime, timedelta

from app import app
from apps.core.data.core import app_get_data
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs, make_inputs_charts_regex, make_inputs_netdata_url,
    parse_netdata_url
)
from apps.core.utils.utils import process_opts, log_inputs
from apps.core.changepoint.core import get_changepoints
from apps.core.plots.lines import plot_lines
from apps.help.popup_changepoints import help

# defaults
app_prefix = 'cp'
DEFAULT_OPTS = 'window=100,diff_min=0.2,smooth_n=1,n_samples=100,sample_len=50,n_results=50,max_points=500'
DEFAULT_CHARTS_REGEX = '.*'
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
tabs = make_tabs(app_prefix, [('Changepoints', 'changepoints')])
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
def run(n_clicks, tab, host, charts_regex, after, before, opts='', netdata_url='', smooth_n=5,
        n_samples=50, sample_len=50, n_results=50, window=100, diff_min=0.05, lw=1, max_points=1000):

    time_start = time.time()

    figs = []

    opts = process_opts(opts)
    smooth_n = int(opts.get('smooth_n', smooth_n))
    n_samples = int(opts.get('n_samples', n_samples))
    sample_len = int(opts.get('sample_len', sample_len))
    n_results = int(opts.get('n_results', n_results))
    window = int(opts.get('window', window))
    lw = int(opts.get('lw', lw))
    diff_min = float(opts.get('diff_min', diff_min))
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
        figs.append(html.Div(dcc.Graph(id='cp-fig-changepoint', figure=make_empty_fig())))
        return figs

    else:

        df = app_get_data(app=app, host=host, charts_regex=charts_regex, after=after, before=before, points=points)
        df = df[[col for col in df.columns if 'uptime' not in col]]
        df = df.rolling(smooth_n).mean()

        df_norm = ((df - df.min()) / (df.max() - df.min()))
        df_norm = df_norm.dropna(how='all', axis=1)
        df_norm = df_norm.dropna(how='all', axis=0)

        df_results = get_changepoints(df_norm, n_samples, sample_len, diff_min, window)
        app.logger.debug(f'df_results.shape = {df_results.shape}')

        for i, row in df_results.sort_values('rank').head(n_results).iterrows():

            metric = row['metric']
            quality_rank = str(int(row['rank']))
            changepoint = row['cp']
            qs = row['qs']
            diff = row['abs_diff']
            fig_changepoint = plot_lines(
                df, [metric], title=f'{quality_rank} - {metric} (qs={qs}, diff={diff})',
                shade_regions=[(changepoint, df.index.max(), 'grey')],
                slider=False, h=300, lw=lw
            )
            figs.append(html.Div(dcc.Graph(id='cp-fig-changepoint', figure=fig_changepoint)))

    app.logger.debug(f'time to finish = {time.time() - time_start}')

    return figs

