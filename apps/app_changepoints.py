# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from netdata_pandas.data import get_data
from am4894plots.plots import plot_lines

from app import app
from .utils.logo import logo
from .utils.defaults import DEFAULT_STYLE, empty_fig
from .utils.utils import process_opts
from .changepoint.core import get_changepoints

DEFAULT_CP_OPTS = 'window=100,diff_min=0.2,smooth_n=5,n_samples=100,sample_len=50,n_results=50'

cp_main_menu = dbc.Col(dbc.ButtonGroup(
    [
        dbc.Button('Home', href='/'),
        dbc.Button('Run', id='cp-btn-run', n_clicks=0),
    ]
))
cp_inputs_host = dbc.FormGroup(
    [
        dbc.Label('host', id='cp-label-host', html_for='cp-input-host', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cp-input-host', value='london.my-netdata.io', type='text', placeholder='host'),
        dbc.Tooltip('Host you would like to pull data from.', target='cp-label-host')
    ]
)
cp_inputs_charts_regex = dbc.FormGroup(
    [
        dbc.Label('charts regex', id='cp-label-charts-regex', html_for='cp-input-charts-regex', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cp-input-charts-regex', value='system.*|apps.*|users.*|groups.*', type='text', placeholder='system.*'),
        dbc.Tooltip('Regex for charts to pull.', target='cp-label-charts-regex')
    ]
)
cp_inputs_after = dbc.FormGroup(
    [
        dbc.Label('after', id='cp-label-after', html_for='cp-input-after', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cp-input-after', value=-1800, type='number', placeholder=-1800),
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
cp_inputs_opts = dbc.FormGroup(
    [
        dbc.Label('options', id='cp-label-opts', html_for='cp-input-opts', style={'margin': '4px', 'padding': '0px'}),
        dbc.Input(id='cp-input-opts', value=DEFAULT_CP_OPTS, type='text', placeholder=DEFAULT_CP_OPTS),
        dbc.Tooltip('list of key values to pass to underlying code.', target='cp-label-opts')
    ]
)
cp_inputs = dbc.Row(
    [
        dbc.Col(cp_inputs_host, width=3),
        dbc.Col(cp_inputs_charts_regex, width=2),
        dbc.Col(cp_inputs_after, width=2),
        dbc.Col(cp_inputs_before, width=2),
        dbc.Col(cp_inputs_opts, width=2),
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
        dbc.Spinner(children=[html.Div(children=html.Div(id='cp-figs'))]),
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
    State('cp-input-opts', 'value'),
)
def cp_run(n_clicks, tab, host, charts_regex, after, before, opts='', smooth_n=5,
        n_samples=50, sample_len=50, n_results=50, window=100, diff_min=0.05):

    figs = []

    opts = process_opts(opts)
    smooth_n = int(opts.get('smooth_n', smooth_n))
    n_samples = int(opts.get('n_samples', n_samples))
    sample_len = int(opts.get('sample_len', sample_len))
    n_results = int(opts.get('n_results', n_results))
    window = int(opts.get('window', window))
    diff_min = float(opts.get('diff_min', diff_min))

    if n_clicks > 0:

        df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
        print(df.shape)
        df = df[[col for col in df.columns if 'uptime' not in col]]
        df = df.rolling(smooth_n).mean()

        df_norm = ((df - df.min()) / (df.max() - df.min()))
        df_norm = df_norm.dropna(how='all', axis=1)
        df_norm = df_norm.dropna(how='all', axis=0)

        df_results = get_changepoints(df_norm, n_samples, sample_len, diff_min, window)

        for i, row in df_results.sort_values('rank').head(n_results).iterrows():

            metric = row['metric']
            quality_rank = str(int(row['rank']))
            changepoint = row['cp']
            qs = row['qs']
            diff = row['abs_diff']
            fig_changepoint = plot_lines(
                df, [metric], title=f'{quality_rank} - {metric} (qs={qs}, diff={diff})', return_p=True,
                show_p=False, shade_regions=[(changepoint, df.index.max(), 'grey')],
                slider=False, h=300,
            )
            figs.append(html.Div(dcc.Graph(id='cp-fig-changepoint', figure=fig_changepoint)))

    else:

        figs.append(html.Div(dcc.Graph(id='cp-fig-changepoint', figure=empty_fig)))

    return figs

