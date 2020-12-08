import os
import logging

from fastapi import FastAPI


# create app
app = FastAPI()

# set up log
log_level = os.getenv("LOG_LEVEL", "INFO")
if log_level == 'DEBUG':
    logging.basicConfig(level = logging.DEBUG)
else:
    logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)


@app.get("/")
async def home():
    return {"Hello": "World"}