# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app
from apps.core.utils.inputs import (
    make_main_menu, make_inputs_host, make_inputs_after, make_inputs_before,
    make_inputs_opts, make_inputs, make_tabs, make_figs, make_inputs_charts_regex, make_inputs_netdata_url,
    parse_netdata_url
)
from apps.core.utils.logo import logo
from apps.core.utils.defaults import DEFAULT_STYLE, make_empty_fig
from apps.core.utils.utils import process_opts, log_inputs
from apps.core.clustering.core import Clusterer
from apps.core.plots.lines import plot_lines, plot_lines_grid
from apps.help.popup_clustering import help

# defaults
app_prefix = 'cl'
DEFAULT_OPTS = 'k=8,smooth_n=10'
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
tabs = make_tabs(app_prefix, [('Cluster Centers', 'centers'), ('Cluster Details', 'details')])
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
def run(n_clicks, tab, host, charts_regex, after, before, opts='', netdata_url='', k=20, lw=1, max_points=1000,
        smooth_n='5'):

    # define some global variables and state change helpers
    global states_previous, states_current, inputs_previous, inputs_current
    global return_error
    global model, valid_clusters
    ctx = dash.callback_context
    inputs_current, states_current = ctx.inputs, ctx.states
    was_button_clicked, has_state_changed, is_initial_run = False, False, True
    if 'states_previous' in globals():
        if set(states_previous.values()) != set(states_current.values()):
            has_state_changed = True
        is_initial_run = False
    if 'inputs_previous' in globals():
        if inputs_current['cl-btn-run.n_clicks'] > inputs_previous['cl-btn-run.n_clicks']:
            was_button_clicked = True
    recalculate = True if was_button_clicked or is_initial_run or has_state_changed else False

    opts = process_opts(opts)
    k = int(opts.get('k', k))
    lw = int(opts.get('lw', lw))
    max_points = int(opts.get('max_points', max_points))
    smooth_n = int(opts.get('smooth_n', smooth_n))
    after = int(datetime.strptime(after, '%Y-%m-%dT%H:%M').timestamp())
    before = int(datetime.strptime(before, '%Y-%m-%dT%H:%M').timestamp())
    points = min(before - after, max_points)
    netdata_url_dict = parse_netdata_url(netdata_url)
    after = netdata_url_dict.get('after', after)
    before = netdata_url_dict.get('before', before)
    host = netdata_url_dict.get('host:port', host)

    log_inputs(app, host, after, before)

    figs = []

    if n_clicks == 0:
        figs.append(html.Div(dcc.Graph(id='cl-fig-changepoint', figure=make_empty_fig())))
        return figs

    # only do expensive work if needed
    if recalculate:

        model = Clusterer([host], charts_regex=charts_regex, after=after, before=before, n_clusters=k, points=points,
                          smooth_n=smooth_n)
        model.run_all()
        valid_clusters = model.df_cluster_meta[model.df_cluster_meta['valid'] == 1].index
        if len(valid_clusters) == 0:
            return_error = True
        else:
            return_error = False

    if return_error:
        figs.append(html.Div(dcc.Graph(id='cl-fig-changepoint', figure=make_empty_fig('No clusters found!'))))
        return figs

    if tab == 'cl-tab-centers':

        titles = [f'{int(x[0])} - n={int(x[1])}, qs={x[2]}' for x in
                  model.df_cluster_meta.loc[valid_clusters].reset_index().values.tolist()]
        fig_centers = plot_lines_grid(
            df=model.df_cluster_centers[valid_clusters],
            subplot_titles=titles, h_each=300,
            legend=False, yaxes_visible=False, xaxes_visible=False,
            lw=lw
        )
        figs.append(html.Div(dcc.Graph(id='cl-fig-centers', figure=fig_centers)))

    else:

        for cluster in valid_clusters:

            title = f"Cluster {cluster} (n={model.cluster_len_dict[cluster]}, score={model.cluster_quality_dict[cluster]})"
            plot_cols = model.cluster_metrics_dict[cluster]
            fig_cluster = plot_lines(
                df=model.df, cols=plot_cols, title=title, slider=False, lw=lw
            )
            figs.append(html.Div(dcc.Graph(id=f'fig-{cluster}', figure=fig_cluster)))

    states_previous = states_current
    inputs_previous = inputs_current

    return figs

