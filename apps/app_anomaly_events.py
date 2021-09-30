# -*- coding: utf-8 -*-
import time

import requests
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from datetime import datetime, timedelta

from app import app
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_metrics, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs, make_inputs_netdata_url, parse_netdata_url,
    make_inputs_charts_regex
)
from apps.core.utils.utils import process_opts, log_inputs
from apps.core.plots.lines import plot_lines, plot_lines_grid
from apps.core.data.core import app_get_data
from apps.help.popup_metrics_explorer import help

# defaults
app_prefix = 'ae'
DEFAULT_OPTS = 'start_buffer=5,end_buffer=1,max_points=1000,ln_top_n=20,hm_top_n=50,hm_w=1200,hm_h=30,ln_h=400'
DEFAULT_CHARTS_REGEX = '\.*'
DEFAULT_AFTER = datetime.strftime(datetime.utcnow() - timedelta(minutes=15), '%Y-%m-%dT%H:%M')
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
layout = html.Div([logo, main_menu, help, inputs, make_figs(f'{app_prefix}-figs')], style=DEFAULT_STYLE)


@app.callback(
    Output(f'{app_prefix}-figs', 'children'),
    Input(f'{app_prefix}-btn-run', 'n_clicks'),
    State(f'{app_prefix}-input-host', 'value'),
    State(f'{app_prefix}-input-charts-regex', 'value'),
    State(f'{app_prefix}-input-after', 'value'),
    State(f'{app_prefix}-input-before', 'value'),
    State(f'{app_prefix}-input-opts', 'value'),
    State(f'{app_prefix}-input-netdata-url', 'value'),
)
def run(n_clicks, host, charts_regex, after, before, opts='', netdata_url='', lw=1,
        max_points=1000, ln_top_n=25, start_buffer=5, end_buffer=1, hm_top_n=50, hm_w=1200, hm_h=30, ln_h=400):

    time_start = time.time()

    # define some global variables and state change helpers
    global states_previous, states_current, inputs_previous, inputs_current
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
    ln_top_n = int(opts.get('ln_top_n', ln_top_n))
    hm_top_n = int(opts.get('hm_top_n', hm_top_n))
    start_buffer = int(opts.get('start_buffer', start_buffer))
    end_buffer = int(opts.get('end_buffer', end_buffer))
    max_points = int(opts.get('max_points', max_points))
    hm_w = int(opts.get('hm_w', hm_w))
    hm_h = int(opts.get('hm_h', hm_h))
    ln_h = int(opts.get('ln_h', ln_h))
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
    points = min(before-after, max_points)
    netdata_url_dict = parse_netdata_url(netdata_url)
    after = netdata_url_dict.get('after', after)
    before = netdata_url_dict.get('before', before)
    after_long = netdata_url_dict.get('after_long', None)
    before_long = netdata_url_dict.get('before_long', None)
    host = netdata_url_dict.get('host:port', host)

    log_inputs(app, host, after, before, points, charts_regex=charts_regex)

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-fig-empty', figure=make_empty_fig())))
        return figs

    if recalculate:

        url_anomaly_events = f"http://{host}/api/v1/anomaly_events?after={after_long}&before={before_long}"
        app.logger.info(url_anomaly_events)
        anomaly_events = requests.get(url_anomaly_events).json()

        for anomaly_event in anomaly_events:
            anomaly_event_start = anomaly_event[0]
            anomaly_event_end = anomaly_event[1]
            anomaly_event_start_ts = pd.Timestamp(datetime.utcfromtimestamp(anomaly_event_start).strftime('%Y-%m-%d %H:%M:%S'))
            anomaly_event_end_ts = pd.Timestamp(datetime.utcfromtimestamp(anomaly_event_end).strftime('%Y-%m-%d %H:%M:%S'))
            anomaly_event_len = anomaly_event_end - anomaly_event_start
            url_anomaly_event = f"http://{host}/api/v1/anomaly_event_info?after={anomaly_event_start}&before={anomaly_event_end}"
            anomaly_event = requests.get(url_anomaly_event).json()
            app.logger.info(url_anomaly_event)
            df_anomaly_event = pd.DataFrame(anomaly_event, columns=['anomaly_rate', 'chart|dim'])
            df_anomaly_event['anomaly_event_start'] = anomaly_event_start
            df_anomaly_event['anomaly_event_end'] = anomaly_event_end
            df_anomaly_event['chart'] = df_anomaly_event['chart|dim'].str.split('|').str[0]
            df_anomaly_event['dim'] = df_anomaly_event['chart|dim'].str.split('|').str[1]
            df_anomaly_event = df_anomaly_event[
                ['anomaly_event_start', 'anomaly_event_end', 'chart|dim', 'chart', 'dim', 'anomaly_rate']]

            charts = df_anomaly_event['chart'].unique().tolist()
            chart_dims = df_anomaly_event['chart|dim'].unique().tolist()[0:(max(ln_top_n, hm_top_n))]
            after = anomaly_event_start - (anomaly_event_len * start_buffer)
            before = anomaly_event_end + (anomaly_event_len * end_buffer)
            after_long = after * 1000
            before_long = before * 1000
            anomaly_event_start_long = anomaly_event_start * 1000
            anomaly_event_end_long = anomaly_event_end * 1000

            df_anomaly_event_raw = app_get_data(app, host=host, charts=charts, after=after, before=before,
                                                points=max_points)
            df_anomaly_event_raw = df_anomaly_event_raw[chart_dims]

            df_anomaly_event_bit = app_get_data(app, host=host, charts=charts, after=after, before=before,
                                                options='anomaly-bit', points=max_points)
            df_anomaly_event_bit = df_anomaly_event_bit[chart_dims]
            df_anomaly_event_bit = df_anomaly_event_bit.add_suffix('_bit')

            df_anomaly_event_data = df_anomaly_event_raw.join(df_anomaly_event_bit)

            heatmap_dims = [f'{dim}_bit' for dim in df_anomaly_event['chart|dim'].head(hm_top_n).values.tolist()]
            df_heatmap = df_anomaly_event_bit[heatmap_dims][anomaly_event_start_ts:anomaly_event_end_ts]
            df_heatmap.columns = [f'(AR={round(x[0]*100,2)}%) {x[1]}' for x in df_anomaly_event[['anomaly_rate', 'chart|dim']].head(hm_top_n).values.tolist()]
            fig = px.imshow(df_heatmap.transpose(), color_continuous_scale='Greens')
            fig.update_layout(
                autosize=False,
                width=hm_w,
                height=len(df_heatmap.columns) * hm_h)
            figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-hm-fig', figure=fig)))

            for chart_dim, anomaly_rate in df_anomaly_event[['chart|dim', 'anomaly_rate']].head(ln_top_n).values.tolist():
                chart = chart_dim.split('|')[0]
                dim = chart_dim.split('|')[1]
                chart_url = f'http://{host}/#;after={after_long};before={before_long};chart={chart};highlight_after={anomaly_event_start_long};highlight_before={anomaly_event_end_long}'
                chart_title = f'{chart_dim} (ar={round(anomaly_rate*100, 2)}%) (<a href="{chart_url}">netdata dashboard</a>)'
                fig = plot_lines(
                    df_anomaly_event_data[[chart_dim]], title=f'Raw Data - {chart_title}', h=ln_h, lw=lw,
                    shade_regions=[(anomaly_event_start_ts, anomaly_event_end_ts, 'grey')], slider=False
                )
                figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-{chart}-{dim}-fig-ts-plot', figure=fig)))
                fig = plot_lines(
                    df_anomaly_event_data[[f'{chart_dim}_bit']], title=f'Anomaly Bit - {chart_title}', h=ln_h, lw=lw,
                    shade_regions=[(anomaly_event_start_ts, anomaly_event_end_ts, 'yellow')], slider=False
                )
                figs.append(html.Div(dcc.Graph(id=f'{app_prefix}-{chart}-{dim}-bit-fig-ts-plot', figure=fig)))

    states_previous = states_current
    inputs_previous = inputs_current

    app.logger.debug(f'time to finish = {time.time() - time_start}')

    return figs
