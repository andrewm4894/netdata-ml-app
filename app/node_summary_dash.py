import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def make_dash_app():
    app_dash = dash.Dash(__name__, requests_pathname_prefix='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    app_dash.layout = html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [1, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5],
                        'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        )
    ])
    return app_dash