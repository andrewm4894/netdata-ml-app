# -*- coding: utf-8 -*-
import logging
import os
from dotenv import load_dotenv

import dash
import dash_bootstrap_components as dbc

load_dotenv()

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
if os.getenv('NETDATAMLAPP_LOG_LEVEL', 'info') == 'debug':
    app.logger.setLevel(logging.DEBUG)
server = app.server
