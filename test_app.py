import os
import pytest
from app import app, init_db, DATABASE_PATH


@pytest.fixture
def client():
    app.config["TESTING"]=True
    init_db()
    with app.test_client() as client:
        yield client
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
def test_add_page_loads(client):
    response = client.get("/add")
    assert response.status_code == 200
def test_stats_page_loads(client):
    response = client.get("/stats")
    assert response.status_code == 200
