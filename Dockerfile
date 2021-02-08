FROM python:3.8

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY ./apps ./apps

COPY ./assets ./assets

COPY ./app.py ./app.py

COPY ./index.py ./index.py

EXPOSE 8050

CMD ["python", "./app.py"]