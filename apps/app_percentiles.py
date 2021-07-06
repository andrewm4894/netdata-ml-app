# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from netdata_pandas.data import get_data

from app import app
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs, make_inputs_charts_regex, make_inputs_netdata_url
)
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.utils import process_opts
from apps.help.popup_percentiles import help

# defaults
app_prefix = 'pc'
DEFAULT_OPTS = 'ref=30m'
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
tabs = make_tabs(app_prefix, [('Percentiles', 'percentiles')])
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
def run(n_clicks, tab, host, charts_regex, after, before, opts, ref='1h', lw=1):

    figs = []

    opts = process_opts(opts)
    ref = opts.get('ref', ref)
    lw = int(opts.get('lw', lw))

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cp-fig', figure=make_empty_fig())))
        return figs

    else:

        if 'h' in ref:
            ref_timedelta = timedelta(hours=int(ref.replace('h', '')))
        elif 'm' in ref:
            ref_timedelta = timedelta(minutes=int(ref.replace('m', '')))
        else:
            ref_timedelta = timedelta(hours=1)

        # get data
        after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
        before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
        df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
        df = df[[col for col in df.columns if 'uptime' not in col]]

        # work out reference window
        ref_before = int(df.index.min().timestamp())
        ref_after = int((df.index.min() - ref_timedelta).timestamp())

        # get the reference data
        df_ref = get_data(hosts=[host], charts_regex=charts_regex, after=ref_after, before=ref_before,
                          index_as_datetime=True)

        # work out percentiles
        df_ref_mean = df_ref.mean()
        df_ref_median = df_ref.median()
        df_ref_p1 = df_ref.quantile(0.01)
        df_ref_p5 = df_ref.quantile(0.05)
        df_ref_p95 = df_ref.quantile(0.95)
        df_ref_p99 = df_ref.quantile(0.99)

        # rank metrics as most interesting based on number of percentile crossovers
        percentile_crossovers = []
        for col in df.columns:
            if col in df_ref.columns:
                p99_crossovers = np.where(df[col] > df_ref_p99.loc[col], 1, 0).sum()
                p95_crossovers = np.where(df[col] > df_ref_p95.loc[col], 1, 0).sum()
                p5_crossovers = np.where(df[col] < df_ref_p5.loc[col], 1, 0).sum()
                p1_crossovers = np.where(df[col] < df_ref_p1.loc[col], 1, 0).sum()
                percentile_crossovers.append([col, p99_crossovers, p95_crossovers, p5_crossovers, p1_crossovers])

        df_percentile_crossovers = pd.DataFrame(
            percentile_crossovers,
            columns=['metric', 'p99_crossovers', 'p95_crossovers', 'p5_crossovers', 'p1_crossovers']
        )
        df_percentile_crossovers['total_crossovers'] = df_percentile_crossovers['p95_crossovers'] + \
                                                       df_percentile_crossovers['p5_crossovers']
        df_percentile_crossovers['crossover_rate'] = round(df_percentile_crossovers['total_crossovers'] / len(df[col]), 2)
        df_percentile_crossovers['metric_rank'] = df_percentile_crossovers['crossover_rate'].rank(ascending=False)
        df_percentile_crossovers = df_percentile_crossovers.set_index('metric')
        df_percentile_crossovers = df_percentile_crossovers.sort_values('metric_rank')

        n = 0

        # plot each metric
        for col in df_percentile_crossovers.sort_values('metric_rank').index:

            n += 1

            if col in df_ref.columns:

                fig = go.Figure()

                # get data
                n_rows = len(df[col])
                raw_data = df[col]
                p99_data = [df_ref_p99.loc[col] for t in range(n_rows)]
                p95_data = [df_ref_p95.loc[col] for t in range(n_rows)]
                mean_data = [df_ref_mean.loc[col] for t in range(n_rows)]
                median_data = [df_ref_median.loc[col] for t in range(n_rows)]
                p5_data = [df_ref_p5.loc[col] for t in range(n_rows)]
                p1_data = [df_ref_p1.loc[col] for t in range(n_rows)]
                crossover_rate = int(round(100 * df_percentile_crossovers.loc[col]['crossover_rate'], 0))

                # skip data that is not interesting
                if df_ref_mean.loc[col] == 0 and df_ref_median.loc[col] == 0 and raw_data.mean() == 0:
                    continue
                # x
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=raw_data, mode='lines', name=col,
                        line=dict(width=lw)
                    )
                )
                # p99
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=p99_data, mode='lines', name=f'p99',
                        line=dict(color='grey', width=lw, dash='dashdot')
                    )
                )
                # p95
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=p95_data, mode='lines', name=f'p95',
                        line=dict(color='grey', width=lw, dash='dash')
                    )
                )
                # mean
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=mean_data, mode='lines', name=f'avg',
                        line=dict(color='black', width=lw)
                    )
                )
                # median
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=median_data, mode='lines', name=f'med',
                        line=dict(color='black', width=lw, dash='dash')
                    )
                )
                # p5
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=p5_data, mode='lines', name=f'p5',
                        line=dict(color='grey', width=lw, dash='dot')
                    )
                )
                # p1
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=p1_data, mode='lines', name=f'p1',
                        line=dict(color='grey', width=lw, dash='dashdot')
                    )
                )
                fig.update_layout(
                    template='simple_white',
                    title=f'{col} - {crossover_rate}% crossover (ref: -{ref_timedelta})',
                    showlegend=False
                )
                figs.append(html.Div(dcc.Graph(id=f'fig-{n}', figure=fig)))

    return figs

