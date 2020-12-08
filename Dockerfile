  
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# set ENV arg
ARG ENV=local

# copy requirements
COPY requirements.txt /app/requirements.txt

# install app requirements
RUN pip install -r /app/requirements.txt

# install pytest and requests for testing
RUN pip install pytest==6.0.1 requests==2.24.0

# copy app folder
COPY ./app /app

# run tests
RUN pytest