import pytest


@pytest.mark.django_db
def test_spa_route_served_with_no_cache(client):
    resp = client.get("/some/client/side/route")
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/html")
    assert "no-cache" in resp["Cache-Control"]


@pytest.mark.django_db
def test_root_served_with_no_cache(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/html")
    assert "no-cache" in resp["Cache-Control"]
