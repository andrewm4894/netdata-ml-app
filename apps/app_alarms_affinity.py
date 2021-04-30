# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app
from apps.core.data.core import make_table
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.inputs import make_main_menu, make_inputs_host, make_inputs_opts, make_inputs_generic, make_inputs
from apps.core.utils.utils import process_opts
from apps.core.alarms_affinity.core import process_basket, make_baskets, itemsets_tooltips, rules_tooltips
from apps.help.popup_alarms_affinity import help

# defaults
app_prefix = 'al'
DEFAULT_OPTS = 'window=1m'

# inputs
main_menu = make_main_menu(app_prefix)
inputs_host = make_inputs_host(app_prefix)
inputs_hours_ago = make_inputs_generic(
    app_prefix, 'hours-ago', 'text', None,
    tooltip_text='How many recent hours of alarms to include.', label_text='hours ago'
)
inputs_last_n = make_inputs_generic(
    app_prefix, 'last-n', 'number', 100,
    tooltip_text='How many recent alarms to include, regardless of when they occurred', label_text='last n'
)
inputs_opts = make_inputs_opts(app_prefix, DEFAULT_OPTS)
inputs = make_inputs([(inputs_host, 3), (inputs_hours_ago, 2), (inputs_last_n, 2), (inputs_opts, 3), (html.Div(''), 2)])

# layout
tabs = dbc.Tabs(
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
        main_menu,
        help,
        inputs,
        tabs,
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
def run(n_clicks, tab, host, hours_ago, last_n, opts='', window='1m', max_n=500, min_support=0.1, min_threshold=0.1):

    # define some global variables and state change helpers
    global states_previous, states_current, inputs_previous, inputs_current
    global alarm_dataset, chart_dataset, when_min, when_max, n_alarms_analyzed
    global itemsets_alarm, rules_alarm, itemsets_chart, rules_chart
    ctx = dash.callback_context
    inputs_current, states_current = ctx.inputs, ctx.states
    was_button_clicked, has_state_changed, is_initial_run = False, False, True
    if 'states_previous' in globals():
        if set(states_previous.values()) != set(states_current.values()):
            has_state_changed = True
        is_initial_run = False
    if 'inputs_previous' in globals():
        if inputs_current['al-btn-run.n_clicks'] > inputs_previous['al-btn-run.n_clicks']:
            was_button_clicked = True
    recalculate = True if was_button_clicked or is_initial_run or has_state_changed else False

    figs = []

    opts = process_opts(opts)
    window = opts.get('window', window)

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='al-fig-empty', figure=make_empty_fig())))
        return figs

    else:

        if recalculate:

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

    states_previous = states_current
    inputs_previous = inputs_current

    return figs

