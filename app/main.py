import os
import logging

import pandas as pd
from netdata_pandas.data import get_data
from fastapi import FastAPI
import fastapi
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.middleware.wsgi import WSGIMiddleware
from node_summary_dash import make_dash_app

log_level = os.getenv("LOG_LEVEL", "INFO")
if log_level == 'DEBUG':
    logging.basicConfig(level = logging.DEBUG)
else:
    logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)


app = FastAPI()
templates = Jinja2Templates('templates')
dash_app = make_dash_app()
app.mount("/dash", WSGIMiddleware(dash_app.server))


@app.get("/liveness")
def liveness():
    return "alive"


@app.get("/readiness")
def readiness():
    return "ready"


@app.get("/")
def home(request: Request):
    data = {'request': request}
    return templates.TemplateResponse('index.html', data)


@app.post("/node-summary")
def node_summary(request: Request, host: str = Form(...)):
    df = get_data(host, ['system.cpu','system.load'], after=-60, before=0)
    context = {
        'request': request, 
        'host': host,
        'df_shape': df.shape
        }
    return templates.TemplateResponse('node-summary.html', context)


@app.get("/dev")
def dev():
    df = get_data('london.my-netdata.io', ['system.cpu','system.load'], after=-60, before=0)
    return fastapi.responses.PlainTextResponse(df.to_string())
