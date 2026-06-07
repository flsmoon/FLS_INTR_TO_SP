import pytest
import app as app_module


@pytest.fixture
def client(monkeypatch, tmp_path):
    db=str(tmp_path/"test.db")
    monkeypatch.setattr(app_module,"DATABASE_PATH",db)
    app_module.init_db()
    app_module.app.config["TESTING"]=True
    with app_module.app.test_client() as c:
        yield c
