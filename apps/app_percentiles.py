# -*- coding: utf-8 -*-

from datetime import timedelta
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from netdata_pandas.data import get_data

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE


main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='btn-run', n_clicks=0),
    ]
))

inputs_host = dbc.FormGroup(
    [
        dbc.Label('Host', id='label-host', html_for='input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='label-host')
    ]
)

inputs_charts_regex = dbc.FormGroup(
    [
        dbc.Label('Charts Regex', id='label-charts-regex', html_for='input-charts-regex', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-charts-regex', value='system.*', type='text', placeholder='system.*'),
        dbc.Tooltip('Regex for charts to pull.', target='label-charts-regex')
    ]
)

inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='label-after', html_for='input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-after', value=-900, type='number', placeholder=-900),
        dbc.Tooltip('"after" as per netdata rest api.', target='label-after')
    ]
)

inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='label-before', html_for='input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='label-before')
    ]
)

inputs_ref = dbc.FormGroup(
    [
        dbc.Label('Ref', id='label-ref', html_for='input-ref', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-ref', value='4h', type='text', placeholder='4h'),
        dbc.Tooltip('Reference window to use e.g 4h compares to previous 4 hours.', target='label-ref')
    ]
)

inputs = dbc.Row(
    [
        dbc.Col(inputs_host, width=3),
        dbc.Col(inputs_charts_regex, width=3),
        dbc.Col(inputs_after, width=2),
        dbc.Col(inputs_before, width=2),
        dbc.Col(inputs_ref, width=1),
        dbc.Col(html.Div(''), width=1)
    ], style={'margin': '0px', 'padding': '0px'}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(label='Percentiles', tab_id='tab-percentiles'),
    ], id='tabs', active_tab='tab-percentiles', style={'margin': '12px', 'padding': '2px'}
)

layout = html.Div(
    [
        logo,
        main_menu,
        inputs,
        tabs,
        html.Div(children=html.Div(id='figs-percentiles')),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('figs-percentiles', 'children'),
    Input('btn-run', 'n_clicks'),
    Input('tabs', 'active_tab'),
    State('input-host', 'value'),
    State('input-charts-regex', 'value'),
    State('input-after', 'value'),
    State('input-before', 'value'),
    State('input-ref', 'value'),
)
def display_value(n_clicks, tab, host, charts_regex, after, before, ref):
    if ref == '4h':
        ref_timedelta = timedelta(hours=4)
    else:
        ref_timedelta = timedelta(hours=1)

    # get data
    df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)

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

    figs = []

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
                    x=df.index, y=raw_data, mode='lines', name='x',
                    line=dict(width=1)
                )
            )
            # p99
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=p99_data, mode='lines', name=f'p99',
                    line=dict(color='grey', width=1, dash='dashdot')
                )
            )
            # p95
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=p95_data, mode='lines', name=f'p95',
                    line=dict(color='grey', width=1, dash='dash')
                )
            )
            # mean
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=mean_data, mode='lines', name=f'avg',
                    line=dict(color='black', width=1)
                )
            )
            # median
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=median_data, mode='lines', name=f'med',
                    line=dict(color='black', width=1, dash='dash')
                )
            )
            # p5
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=p5_data, mode='lines', name=f'p5',
                    line=dict(color='grey', width=1, dash='dot')
                )
            )
            # p1
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=p1_data, mode='lines', name=f'p1',
                    line=dict(color='grey', width=1, dash='dashdot')
                )
            )
            fig.update_layout(
                template='simple_white',
                title=f'{col} - {crossover_rate}% crossover (ref: -{ref_timedelta})'
            )
            figs.append(html.Div(dcc.Graph(id=f'fig-{n}', figure=fig)))

    return figs

