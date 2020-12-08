from fastapi.testclient import TestClient
import pytest
import json

from app.main import app


client = TestClient(app)


def test_alive():

    url = f'http://127.0.0.1/liveness'
    payload = {}
    payload = json.dumps(payload)
    response = client.get(url=url, data=payload)
    assert response.status_code == 200
    assert response.text == '"alive"'


def test_ready():

    url = f'http://127.0.0.1/readiness'
    payload = {}
    payload = json.dumps(payload)
    response = client.get(url=url, data=payload)
    assert response.status_code == 200
    assert response.text == '"ready"' 