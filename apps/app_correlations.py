# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from app import app
from .data.core import make_table
from .correlations.core import get_df_corr, make_df_corr_long
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, make_empty_fig
from .utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_charts_regex, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs
)
from .utils.utils import process_opts
from .help_popup.correlations import help, toggle_help

# defaults
app_prefix = 'cor'
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
inputs = make_inputs([(inputs_host, 6), (inputs_after, 3), (inputs_before, 3), (inputs_charts_regex, 6), (inputs_opts, 6)])

# layout
tabs = make_tabs(
    app_prefix,
    [
        ('Correlation Heatmap', 'correlation-heatmap'),
        ('Correlation Bar Plot', 'correlation-bar'),
        ('Correlation Changes', 'correlation-changes')
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
def run(n_clicks, tab, host, charts_regex, after, before, opts, freq='10s', w='1200'):

    # define some global variables and state change helpers
    global states_previous, states_current, inputs_previous, inputs_current
    global df, df_corr_long, df_ref_corr, df_ref_corr_long, df_corr_changes
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
    freq = opts.get('freq', freq)
    w = int(opts.get('w', w))

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cor-fig', figure=make_empty_fig())))
        return figs

    if recalculate:

        # get data
        df = get_df_corr(
            hosts=[host],
            charts_regex=charts_regex,
            after=int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp()),
            before=int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp()),
            index_as_datetime=True, freq=freq
        )
        df_corr_long = make_df_corr_long(df)
        window = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp()) - int(
            datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
        after_ref = int((datetime.strptime(after, '%Y-%m-%dT%H:%M') - timedelta(seconds=window)).timestamp())
        before_ref = int((datetime.strptime(before, '%Y-%m-%dT%H:%M') - timedelta(seconds=window)).timestamp())
        df_ref_corr = get_df_corr([host], charts_regex, after_ref, before_ref, True, freq)
        df_ref_corr_long = make_df_corr_long(df_ref_corr)

        df_corr_changes = df_corr_long.merge(df_ref_corr_long, on='Dimension Pair', suffixes=('', ' Previous'))
        df_corr_changes['Diff'] = df_corr_changes['Correlation Previous'] - df_corr_changes['Correlation']
        df_corr_changes['Diff Abs'] = abs(df_corr_changes['Diff'])
        df_corr_changes = round(df_corr_changes.sort_values('Diff Abs', ascending=False), 2)

    if tab == f'{app_prefix}-tab-correlation-heatmap':

        fig = px.imshow(df, color_continuous_scale='Greens')
        fig.update_layout(
            autosize=False,
            width=w,
            height=len(df.columns) * 25)
        figs.append(html.Div(dcc.Graph(id='cor-fig', figure=fig)))

    elif tab == f'{app_prefix}-tab-correlation-bar':

        fig = go.Figure(go.Bar(
            x=df_corr_long['Correlation Abs'],
            y=df_corr_long['Dimension Pair'],
            marker_color=np.where(df_corr_long['Pos or Neg'] == '+', 'forestgreen', 'red'),
            text=df_corr_long['Correlation Abs'],
            textposition='auto',
            orientation='h'))
        fig.update_layout(
            autosize=False,
            width=w,
            height=len(df_corr_long) * 25
        )
        figs.append(html.Div(dcc.Graph(id='cor-bar-fig', figure=fig)))

    elif tab == f'{app_prefix}-tab-correlation-changes':

        fig = go.Figure(
            data=go.Scatter(
                x=df_corr_changes['Correlation Previous'],
                y=df_corr_changes['Correlation'],
                mode='markers',
                text=df_corr_changes['Dimension Pair'],
                marker=dict(
                    size=10,
                    color=df_corr_changes['Diff Abs'],
                    colorscale='Viridis',
                    showscale=True
                )
            )
        )
        fig.update_layout(
            template='simple_white',
            xaxis_title="Correlation Previous",
            yaxis_title="Correlation",
            legend_title="Correlation Abs Diff",
        )
        figs.append(html.Div(dcc.Graph(id='cor-fig', figure=fig)))

        fig = make_table(df_corr_changes[['Dimension Pair', 'Correlation Previous', 'Correlation', 'Diff']], f'{app_prefix}-tbl-data')
        figs.append(html.Div(children=[fig], style={"margin": "6px", "padding": "6px"}))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs

