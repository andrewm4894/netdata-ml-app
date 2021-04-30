# -*- coding: utf-8 -*-

import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app
from .defaults import DEFAULT_STYLE

logo = html.Div(
    [
        dbc.Col(html.Img(src=app.get_asset_url('logo.svg')), width=4, style=DEFAULT_STYLE),
        dbc.Col(html.Pre('experimental machine learning app', style={'color': '#999FA4'})),
    ])
