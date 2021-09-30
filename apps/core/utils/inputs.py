import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from urllib.parse import urlparse
import re

from app import app
from apps.core.config.config import get_config

app_config_found, app_config = get_config()
app_config_hosts = app_config.get('hosts')

DEFAULT_HOSTS_DROPDOWN = [{'label': h, 'value': h} for h in app_config_hosts]


def make_main_menu(prefix):
    main_menu = dbc.Col(dbc.ButtonGroup(
        [
            dbc.Button('Home', href='/'),
            dbc.Button("Help", id=f'{prefix}-help-open'),
            dbc.Button('Run', id=f'{prefix}-btn-run', n_clicks=0),
        ]
    ))
    return main_menu


def make_inputs_host(prefix):
    inputs_host = dbc.FormGroup(
        [
            dbc.Label('host', id=f'{prefix}-label-host', html_for=f'{prefix}-input-host', style={'margin': '4px', 'padding': '0px'}),
            (
                dcc.Dropdown(id=f'{prefix}-input-host', placeholder='host', options=DEFAULT_HOSTS_DROPDOWN,
                             value=DEFAULT_HOSTS_DROPDOWN[0]['value'], optionHeight=60)
                if app_config_found
                else
                dbc.Input(id=f'{prefix}-input-host', value='london.my-netdata.io', type='text', placeholder='host')
            ),
            dbc.Tooltip('Host you would like to pull data from.', target=f'{prefix}-label-host')
        ]
    )
    return inputs_host


def make_inputs_metrics(prefix, default_metrics, tooltip_text='Metrics to explore.', label_text='metrics'):
    inputs_metrics = dbc.FormGroup(
        [
            dbc.Label(label_text, id=f'{prefix}-label-metrics', html_for=f'{prefix}-input-metrics',
                      style={'margin': '4px', 'padding': '0px'}),
            dbc.Input(id=f'{prefix}-input-metrics', value=default_metrics, type='text', placeholder=default_metrics),
            dbc.Tooltip(tooltip_text, target=f'{prefix}-label-metrics')
        ]
    )
    return inputs_metrics


def make_inputs_charts_regex(prefix, default_charts_regex, tooltip_text='Regex for charts to pull.', label_text='charts regex'):
    inputs_charts_regex = dbc.FormGroup(
        [
            dbc.Label(label_text, id=f'{prefix}-label-charts-regex', html_for=f'{prefix}-input-charts-regex',
                      style={'margin': '4px', 'padding': '0px'}),
            dbc.Input(id=f'{prefix}-input-charts-regex', value=default_charts_regex, type='text',
                      placeholder=default_charts_regex),
            dbc.Tooltip(tooltip_text, target=f'{prefix}-label-charts-regex')
        ]
    )
    return inputs_charts_regex


def make_inputs_after(prefix, default_after, tooltip_text='"after" as per netdata rest api.', label_text='after'):
    inputs_after = dbc.FormGroup(
        [
            dbc.Label(label_text, id=f'{prefix}-label-after', html_for=f'{prefix}-input-after',
                      style={'margin': '4px', 'padding': '0px'}),
            dbc.Input(id=f'{prefix}-input-after', value=default_after, type='datetime-local'),
            dbc.Tooltip(tooltip_text, target=f'{prefix}-label-after')
        ]
    )
    return inputs_after


def make_inputs_before(prefix, default_before, tooltip_text='"before" as per netdata rest api.', label_text='before'):
    inputs_before = dbc.FormGroup(
        [
            dbc.Label(label_text, id=f'{prefix}-label-before', html_for=f'{prefix}-input-before',
                      style={'margin': '4px', 'padding': '0px'}),
            dbc.Input(id=f'{prefix}-input-before', value=default_before, type='datetime-local'),
            dbc.Tooltip(tooltip_text, target=f'{prefix}-label-before')
        ]
    )
    return inputs_before


def make_inputs_opts(prefix, default_opts, tooltip_text='List of optional key values to pass to underlying code.',
                     label_text='options'):
    inputs_opts = dbc.FormGroup(
        [
            dbc.Label(label_text, id=f'{prefix}-label-opts', html_for=f'{prefix}-input-opts',
                      style={'margin': '4px', 'padding': '0px'}),
            dbc.Input(id=f'{prefix}-input-opts', value=default_opts, type='text', placeholder=default_opts),
            dbc.Tooltip(tooltip_text, target=f'{prefix}-label-opts')
        ]
    )
    return inputs_opts


def make_inputs_netdata_url(prefix, default_netdata_url='', tooltip_text='Url of interest from a netdata dashboard.',
                     label_text='netdata url'):
    inputs_netdata_url = dbc.FormGroup(
        [
            dbc.Label(label_text, id=f'{prefix}-label-netdata-url', html_for=f'{prefix}-input-netdata-url',
                      style={'margin': '4px', 'padding': '0px'}),
            dbc.Input(id=f'{prefix}-input-netdata-url', value=default_netdata_url, type='text', placeholder=default_netdata_url),
            dbc.Tooltip(tooltip_text, target=f'{prefix}-label-netdata-url')
        ]
    )
    return inputs_netdata_url


def make_inputs(inputs_list):
    return dbc.Row(
        [dbc.Col(i[0], width=i[1]) for i in inputs_list], style={'margin': '0px', 'padding': '0px'}
    )


def make_inputs_generic(prefix, suffix, input_type, default_value, tooltip_text, label_text):
    inputs_generic = dbc.FormGroup(
        [
            dbc.Label(label_text, id=f'{prefix}-label-{suffix}', html_for=f'{prefix}-input-{suffix}',
                      style={'margin': '4px', 'padding': '0px'}),
            dbc.Input(id=f'{prefix}-input-{suffix}', value=default_value, type=input_type, placeholder=default_value),
            dbc.Tooltip(tooltip_text, target=f'{prefix}-label-{suffix}')
        ]
    )
    return inputs_generic


def make_tabs(prefix, tab_list, active_tab_num=0):
    tabs = dbc.Tabs(
        [dbc.Tab(label=t[0], tab_id=f'{prefix}-tab-{t[1]}') for t in tab_list],
        id=f'{prefix}-tabs', active_tab=f'{prefix}-tab-{tab_list[active_tab_num][1]}',
        style={'margin': '12px', 'padding': '2px'}
    )
    return tabs


def make_figs(id):
    figs = dbc.Spinner(children=[html.Div(children=html.Div(id=id))])
    return figs


def make_card(button, text, logo):
    card = dbc.Card(
        [
            dbc.CardImg(src=app.get_asset_url(logo), top=True),
            dbc.CardBody([button, dcc.Markdown(text, style={"margin": "4px", "padding": "0px"})]),
        ],
        style={"margin": "4px", "padding": "4px"},
    )
    return card


def parse_netdata_url(url):
    if url.startswith('http'):
        url_parsed = urlparse(url)
        url_dict = {
            'host': url_parsed.hostname,
            'port': url_parsed.port,
            'host:port': f'{url_parsed.hostname}:{url_parsed.port}' if url_parsed.port else url_parsed.hostname,
            'fragments': {frag.split('=')[0]: frag.split('=')[1] for frag in url_parsed.fragment.split(';') if '=' in frag}
        }
    else:
        url_dict = {
            'fragments': {frag.split('=')[0]: frag.split('=')[1] for frag in url.split(';') if
                          '=' in frag}
        }

    if 'after' in url_dict['fragments']:
        url_dict['after_long'] = int(int(url_dict['fragments']['after']))
        url_dict['after'] = int(int(url_dict['fragments']['after']) / 1000)
    if 'before' in url_dict['fragments']:
        url_dict['before_long'] = int(int(url_dict['fragments']['before']))
        url_dict['before'] = int(int(url_dict['fragments']['before']) / 1000)

    if 'highlight_after' in url_dict['fragments']:
        url_dict['highlight_after_long'] = int(int(url_dict['fragments']['highlight_after']))
        url_dict['highlight_after'] = int(int(url_dict['fragments']['highlight_after']) / 1000)
    if 'highlight_before' in url_dict['fragments']:
        url_dict['highlight_before_long'] = int(int(url_dict['fragments']['highlight_before']))
        url_dict['highlight_before'] = int(int(url_dict['fragments']['highlight_before']) / 1000)

    child_host = re.search('/host/(.*?)/', url)
    child_host = child_host.group(1) if child_host else None
    print(child_host)
    if child_host:
        url_dict['child_host'] = child_host
        url_dict['host:port'] = url_dict['host:port'] + f'/host/{child_host}'

    return url_dict


