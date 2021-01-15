# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from netdata_pandas.data import get_data
from am4894plots.plots import plot_lines
import plotly.graph_objects as go

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, empty_fig
from .changepoint.core import get_changepoints


cp_main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='cp-btn-run', n_clicks=0),
    ]
))
cp_inputs_host = dbc.FormGroup(
    [
        dbc.Label('Host', id='cp-label-host', html_for='cp-input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cp-input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='cp-label-host')
    ]
)
cp_inputs_charts_regex = dbc.FormGroup(
    [
        dbc.Label('Charts Regex', id='cp-label-charts-regex', html_for='cp-input-charts-regex', style={'margin': '4px', 'padding': '0px'}),
        #dbc.Input(id='cp-input-charts-regex', value='^(?!.*uptime).*$', type='text', placeholder='system.*'),
        dbc.Input(id='cp-input-charts-regex', value='system.*', type='text', placeholder='system.*'),
        dbc.Tooltip('Regex for charts to pull.', target='cp-label-charts-regex')
    ]
)
cp_inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='cp-label-after', html_for='cp-input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cp-input-after', value=-900, type='number', placeholder=-900),
        dbc.Tooltip('"after" as per netdata rest api.', target='cp-label-after')
    ]
)
cp_inputs_before = dbc.FormGroup(
    [
        dbc.Label('before', id='cp-label-before', html_for='cp-input-before', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cp-input-before', value=0, type='number', placeholder=0),
        dbc.Tooltip('"before" as per netdata rest api.', target='cp-label-before')
    ]
)
cp_inputs = dbc.Row(
    [
        dbc.Col(cp_inputs_host, width=3),
        dbc.Col(cp_inputs_charts_regex, width=3),
        dbc.Col(cp_inputs_after, width=2),
        dbc.Col(cp_inputs_before, width=2),
        dbc.Col(html.Div(''), width=1)
    ], style={'margin': '0px', 'padding': '0px'}
)
cp_tabs = dbc.Tabs(
    [
        dbc.Tab(label='Changepoints', tab_id='cp-tab-changepoints'),
    ], id='cp-tabs', active_tab='cp-tab-changepoints', style={'margin': '12px', 'padding': '2px'}
)
layout = html.Div(
    [
        logo,
        cp_main_menu,
        cp_inputs,
        cp_tabs,
        html.Div(children=html.Div(id='cp-figs')),
    ], style=DEFAULT_STYLE
)


@app.callback(
    Output('cp-figs', 'children'),
    Input('cp-btn-run', 'n_clicks'),
    Input('cp-tabs', 'active_tab'),
    State('cp-input-host', 'value'),
    State('cp-input-charts-regex', 'value'),
    State('cp-input-after', 'value'),
    State('cp-input-before', 'value'),
)
def run(n_clicks, tab, host, charts_regex, after, before, smooth_n=5, n_samples=25, sample_len=50, n_results=20):
    figs = []
    if n_clicks > 0:
        df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
        df = df[[col for col in df.columns if 'uptime' not in col]]
        df = df.rolling(smooth_n).mean()
        df_norm = ((df - df.min()) / (df.max() - df.min()))
        df_norm = df_norm.dropna(how='all', axis=1)
        df_norm = df_norm.dropna(how='all', axis=0)
        df_results = get_changepoints(df_norm, n_samples, sample_len)
        for i, row in df_results.head(n_results).iterrows():
            metric = row['metric']
            quality_score = row['quality_score']
            quality_rank = str(int(row['quality_rank']))
            changepoint = row['changepoint']
            abs_mean_pct_diff = row['abs_mean_pct_diff']
            title = f'{metric} - rank={quality_rank}, qs={quality_score}'
            if quality_score <= 0.1 and abs_mean_pct_diff >= 0.3:
                fig_changepoint = plot_lines(
                    df, [metric], title=title, return_p=True, show_p=False,
                    shade_regions=[(changepoint, df.index.max(), 'grey')], slider=False
                )
                figs.append(html.Div(dcc.Graph(id='cp-fig-changepoint', figure=fig_changepoint)))
    else:
        figs.append(html.Div(dcc.Graph(id='cp-fig-changepoint', figure=empty_fig)))

    return figs

