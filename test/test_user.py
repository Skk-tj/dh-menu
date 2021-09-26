import app
import pytest


@pytest.fixture
def client():
    flask_app = app.create_app()
    flask_app.config['TESTING'] = True

    with flask_app.test_client() as client:
        yield client


def test_top_page(client):
    res = client.get("/")
    assert res.status_code == 200


def test_invalid_week(client):
    res = client.get("/abc")
    assert res.status_code == 400


def test_with_week(client):
    res = client.get("/2021-W10")
    assert res.status_code == 200


def test_with_invalid_week(client):
    res = client.get("/2021-W9999")
    assert res.status_code == 400
