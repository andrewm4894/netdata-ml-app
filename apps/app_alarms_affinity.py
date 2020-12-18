# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from netdata_pandas.data import get_alarm_log
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules

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

inputs_hours_ago = dbc.FormGroup(
    [
        dbc.Label('Hours Ago', id='label-hours-ago', html_for='input-hours-ago', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-hours-ago', value=None, type='number', placeholder=None),
        dbc.Tooltip('How many recent hours of alarms to include.', target='label-hours-ago')
    ]
)

inputs_last_n = dbc.FormGroup(
    [
        dbc.Label('Last n', id='label-last-n', html_for='input-last-n', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-last-n', value=100, type='number', placeholder=100),
        dbc.Tooltip('How many recent alarms to include, regardless of when they occurred', target='label-last-n')
    ]
)

inputs_window = dbc.FormGroup(
    [
        dbc.Label('Window', id='label-window', html_for='input-window', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='input-window', value='1m', type='text', placeholder='1m'),
        dbc.Tooltip('Window around alarms in within which to group into a "basket".', target='label-window')
    ]
)

inputs = dbc.Row(
    [
        dbc.Col(inputs_host, width=3),
        dbc.Col(inputs_hours_ago, width=3),
        dbc.Col(inputs_last_n, width=2),
        dbc.Col(inputs_window, width=2),
        dbc.Col(html.Div(''), width=2)
    ], style={'margin': '0px', 'padding': '0px'}
)

tabs = dbc.Tabs(
    [
        dbc.Tab(label='Tables', tab_id='tab-tables'),
    ], id='tabs', active_tab='tab-tables', style={'margin': '12px', 'padding': '2px'}
)

layout = html.Div(
    [
        logo,
        main_menu,
        inputs,
        tabs,
        html.Div(children=html.Div(id='figs-tables')),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('figs-tables', 'children'),
    Input('btn-run', 'n_clicks'),
    Input('tabs', 'active_tab'),
    State('input-host', 'value'),
    State('input-hours-ago', 'value'),
    State('input-last-n', 'value'),
    State('input-window', 'value'),
)
def display_value(n_clicks, tab, host, hours_ago, last_n, window, max_n=500, min_support=0.1, min_threshold=0.1):
    # get alarm log data
    df = get_alarm_log(host)
    df = df[df['status'].isin(['WARNING', 'CRITICAL'])]
    df = df.sort_values('when')

    if hours_ago:
        df = df[df['when'] >= (datetime.now() - timedelta(hours=hours_ago))]
    if last_n:
        df = df.tail(last_n).copy()

    # make transactions dataset
    td = pd.Timedelta(window)
    f_alarm = lambda x, y: df.loc[df['when'].between(y - td, y + td), 'name'].tolist()
    df['alarm_basket'] = [f_alarm(k, v) for k, v in df['when'].items()]
    f_chart = lambda x, y: df.loc[df['when'].between(y - td, y + td), 'chart'].tolist()
    df['chart_basket'] = [f_chart(k, v) for k, v in df['when'].items()]

    if max_n:
        if len(df) > max_n:
            df = df.sample(max_n)
            print(df.shape)

    alarm_dataset = df['alarm_basket'].values.tolist()
    chart_dataset = df['chart_basket'].values.tolist()

    # get some variables to print later
    n_alarms_analyzed = len(alarm_dataset)
    when_min = df['when'].min()
    when_max = df['when'].max()

    # alarm
    te_alarm = TransactionEncoder()
    te_ary_alarm = te_alarm.fit(alarm_dataset).transform(alarm_dataset)
    df_alarm_tx = pd.DataFrame(te_ary_alarm, columns=te_alarm.columns_)
    itemsets_alarm = fpgrowth(df_alarm_tx, min_support=min_support, use_colnames=True).sort_values('support',
                                                                                                   ascending=False)
    rules_alarm = association_rules(itemsets_alarm, metric="confidence", min_threshold=min_threshold).sort_values(
        'support', ascending=False)

    # chart
    te_chart = TransactionEncoder()
    te_ary_chart = te_chart.fit(chart_dataset).transform(chart_dataset)
    df_chart_tx = pd.DataFrame(te_ary_chart, columns=te_chart.columns_)
    itemsets_chart = fpgrowth(df_chart_tx, min_support=min_support, use_colnames=True).sort_values('support',
                                                                                                   ascending=False)
    rules_chart = association_rules(itemsets_chart, metric="confidence", min_threshold=min_threshold).sort_values(
        'support', ascending=False)



    figs = []

    # info
    figs.append(html.Div(f'\n{n_alarms_analyzed} alarms analyzed (spanning {when_min} to {when_max})'))

    # alarm itemsets
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(itemsets_alarm.columns), align='left'),
        cells=dict(values=[itemsets_alarm['support'], itemsets_alarm['itemsets'].astype('unicode')], align='left'))
    ])
    fig.update_layout(title_text='Alarm Itemsets')
    figs.append(html.Div(dcc.Graph(id=f'fig-table-itemsets-alarm', figure=fig)))

    # alarm rules
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(rules_alarm.columns), align='left'),
        cells=dict(values=[
            rules_alarm['antecedents'].astype('unicode'), rules_alarm['consequents'].astype('unicode'), rules_alarm['antecedent support'],
            rules_alarm['consequent support'], rules_alarm['support'], rules_alarm['confidence'],
            rules_alarm['lift'], rules_alarm['leverage'], rules_alarm['conviction']
        ],
        align='left'))
    ])
    fig.update_layout(title_text='Alarm Rules')
    figs.append(html.Div(dcc.Graph(id=f'fig-table-rules-alarm', figure=fig)))

    # chart itemsets
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(itemsets_chart.columns), align='left'),
        cells=dict(values=[itemsets_chart['support'], itemsets_chart['itemsets'].astype('unicode')], align='left'))
    ])
    fig.update_layout(title_text='Chart Itemsets')
    figs.append(html.Div(dcc.Graph(id=f'fig-table-itemsets-chart', figure=fig)))

    # chart rules
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(rules_chart.columns), align='left'),
        cells=dict(values=[
            rules_chart['antecedents'].astype('unicode'), rules_chart['consequents'].astype('unicode'),
            rules_chart['antecedent support'],
            rules_chart['consequent support'], rules_chart['support'], rules_chart['confidence'],
            rules_chart['lift'], rules_chart['leverage'], rules_chart['conviction']
        ],
            align='left'))
    ])
    fig.update_layout(title_text='Chart Rules')
    figs.append(html.Div(dcc.Graph(id=f'fig-table-rules-chart', figure=fig)))

    return figs

