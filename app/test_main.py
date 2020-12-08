from fastapi.testclient import TestClient
import pytest
import json

from .main import app


client = TestClient(app)


def test_main():

    url = f'http://127.0.0.1/'
    payload = {}
    payload = json.dumps(payload)
    response = client.get(url=url, data=payload)

    assert response.status_code == 200
    assert response.text == '{"Hello":"World"}' 