import dash_bootstrap_components as dbc
import dash_core_components as dcc

from apps.config.config import get_config

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
                             value=DEFAULT_HOSTS_DROPDOWN[0]['value'])
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


def make_inputs(inputs_host, inputs_metrics, inputs_after, inputs_before, inputs_opts):
    return dbc.Row(
        [
            dbc.Col(inputs_host, width=3),
            dbc.Col(inputs_metrics, width=3),
            dbc.Col(inputs_after, width=3),
            dbc.Col(inputs_before, width=3),
            dbc.Col(inputs_opts, width=6),
        ], style={'margin': '0px', 'padding': '0px'}
    )

