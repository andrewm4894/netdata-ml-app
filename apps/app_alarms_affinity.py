# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, empty_fig, make_empty_fig
from .utils.utils import process_opts
from .alarms_affinity.core import process_basket, make_baskets, make_table, itemsets_tooltips, rules_tooltips

DEFAULT_AL_OPTS = 'window=1m'

al_main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='al-btn-run', n_clicks=0),
    ]
))
al_inputs_host = dbc.FormGroup(
    [
        dbc.Label('host', id='al-label-host', html_for='al-input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='al-input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='al-label-host')
    ]
)
al_inputs_hours_ago = dbc.FormGroup(
    [
        dbc.Label('hours ago', id='al-label-hours-ago', html_for='al-input-hours-ago', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='al-input-hours-ago', value=None, type='number', placeholder=None),
        dbc.Tooltip('How many recent hours of alarms to include.', target='al-label-hours-ago')
    ]
)
al_inputs_last_n = dbc.FormGroup(
    [
        dbc.Label('last n', id='al-label-last-n', html_for='al-input-last-n', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='al-input-last-n', value=100, type='number', placeholder=100),
        dbc.Tooltip('How many recent alarms to include, regardless of when they occurred', target='al-label-last-n')
    ]
)
al_inputs_opts = dbc.FormGroup(
    [
        dbc.Label('options', id='al-label-opts', html_for='al-input-opts', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='al-input-opts', value=DEFAULT_AL_OPTS, type='text', placeholder=DEFAULT_AL_OPTS),
        dbc.Tooltip('list of key values to pass to underlying code.', target='al-label-opts')
    ]
)
al_inputs = dbc.Row(
    [
        dbc.Col(al_inputs_host, width=3),
        dbc.Col(al_inputs_hours_ago, width=2),
        dbc.Col(al_inputs_last_n, width=2),
        dbc.Col(al_inputs_opts, width=3),
        dbc.Col(html.Div(''), width=2)
    ], style={'margin': '0px', 'padding': '0px'}
)
al_tabs = dbc.Tabs(
    [
        dbc.Tab(label='Alarm Itemsets', tab_id='al-tab-alarm-itemsets'),
        dbc.Tab(label='Alarm Rules', tab_id='al-tab-alarm-rules'),
        dbc.Tab(label='Chart Itemsets', tab_id='al-tab-chart-itemsets'),
        dbc.Tab(label='Chart Rules', tab_id='al-tab-chart-rules'),
    ], id='al-tabs', active_tab='al-tab-alarm-itemsets', style={'margin': '12px', 'padding': '2px'}
)
layout = html.Div(
    [
        logo,
        al_main_menu,
        al_inputs,
        al_tabs,
        dbc.Spinner(children=[html.Div(children=html.Div(id='al-figs-tables'))]),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('al-figs-tables', 'children'),
    Input('al-btn-run', 'n_clicks'),
    Input('al-tabs', 'active_tab'),
    State('al-input-host', 'value'),
    State('al-input-hours-ago', 'value'),
    State('al-input-last-n', 'value'),
    State('al-input-opts', 'value'),
)
def al_run(n_clicks, tab, host, hours_ago, last_n, opts='', window='1m', max_n=500, min_support=0.1, min_threshold=0.1):

    figs = []

    opts = process_opts(opts)
    window = opts.get('window', window)

    al_ctx = dash.callback_context

    global al_states_previous
    global al_states_current
    global al_inputs_previous
    global al_inputs_current
    global al_model
    global al_valid_clusters

    al_states_current = al_ctx.states
    al_inputs_current = al_ctx.inputs

    if n_clicks == 0:

        figs.append(html.Div(dcc.Graph(id='al-fig-empty', figure=empty_fig)))

    else:

        alarm_dataset, chart_dataset, when_min, when_max = make_baskets(host, hours_ago, last_n, window, max_n)

        # get some variables to print later
        n_alarms_analyzed = len(alarm_dataset)

        # alarm
        itemsets_alarm, rules_alarm = process_basket(alarm_dataset, min_support, min_threshold)

        # chart
        itemsets_chart, rules_chart = process_basket(chart_dataset, min_support, min_threshold)

        if tab == 'al-tab-alarm-itemsets':

            fig = make_table(itemsets_alarm, 'al-tbl-alarm-itemsets', itemsets_tooltips)
            figs.append(html.Div(children=[fig], style={"margin": "6px", "padding": "6px"}))

        elif tab == 'al-tab-alarm-rules':

            fig = make_table(rules_alarm, 'al-tbl-alarm-rules', rules_tooltips)
            figs.append(html.Div(children=[fig], style={"margin": "6px", "padding": "6px"}))

        elif tab == 'al-tab-chart-itemsets':

            fig = make_table(itemsets_chart, 'al-tbl-chart-itemsets', itemsets_tooltips)
            figs.append(html.Div(children=[fig], style={"margin": "6px", "padding": "6px"}))

        elif tab == 'al-tab-chart-rules':

            fig = make_table(rules_chart, 'al-tbl-chart-rules', rules_tooltips)
            figs.append(html.Div(children=[fig], style={"margin": "6px", "padding": "6px"}))

        else:

            figs = [html.Div(dcc.Graph(id='al-fig-empty', figure=make_empty_fig('Error!')))]

        figs.append(
            html.Div(
                dbc.Alert(
                    f'\n{n_alarms_analyzed} alarms analyzed (spanning {when_min} to {when_max})',
                    color='light'
                ),
                style={"margin": "6px", "padding": "6px"}
            )
        )

    al_states_previous = al_states_current
    al_inputs_previous = al_inputs_current

    return figs

