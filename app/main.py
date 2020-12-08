import os
import logging

import pandas as pd
from netdata_pandas.data import get_data
from fastapi import FastAPI
import fastapi
from starlette.templating import Jinja2Templates
from starlette.requests import Request

templates = Jinja2Templates('templates')
app = FastAPI()

# set up log
log_level = os.getenv("LOG_LEVEL", "INFO")
if log_level == 'DEBUG':
    logging.basicConfig(level = logging.DEBUG)
else:
    logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)


@app.get("/liveness")
async def liveness():
    return "alive"


@app.get("/readiness")
async def readiness():
    return "ready"


@app.get("/")
async def home(request: Request):
    data = {'request': request}
    return templates.TemplateResponse('home.html', data)


@app.get("/dev")
async def dev():
    df = get_data('london.my-netdata.io', ['system.cpu','system.load'], after=-60, before=0)
    return fastapi.responses.PlainTextResponse(df.to_string())
