def test_index(client):
    r = client.get("/")
    assert r.status_code == 200


def test_add_page(client):
    r = client.get("/add")
    assert r.status_code == 200


def test_add_habit(client):
    client.post("/add", data={"title": "Читать книгу"})
    r = client.get("/")
    assert "Читать книгу" in r.data.decode("utf-8")


def test_add_empty_title(client):
    r = client.post("/add", data={"title": ""})
    assert r.status_code == 302


def test_complete_habit(client):
    client.post("/add", data={"title": "Бегать"})
    r = client.post("/complete/1")
    assert r.status_code == 302


def test_complete_twice(client):
    client.post("/add", data={"title": "Пить воду"})
    client.post("/complete/1")
    r = client.post("/complete/1")
    assert r.status_code == 302


def test_delete_habit(client):
    client.post("/add", data={"title": "Медитация"})
    client.post("/delete/1")
    r = client.get("/")
    assert "Медитация" not in r.data.decode("utf-8")


def test_stats_page(client):
    r = client.get("/stats")
    assert r.status_code == 200


def test_stats_shows_habit(client):
    client.post("/add", data={"title": "Спорт"})
    r = client.get("/stats")
    assert "Спорт" in r.data.decode("utf-8")
