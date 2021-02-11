FROM python:3.8-slim-buster

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./apps ./apps
COPY ./assets ./assets
COPY app.py ./
COPY index.py ./
COPY app_config.yml ./

CMD [ "gunicorn", "--workers=2", "--threads=1", "-b 0.0.0.0:29999", "index:server"]