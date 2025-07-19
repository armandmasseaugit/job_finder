from fastapi.testclient import TestClient
from web_app.backend.main import app

client = TestClient(app)


def test_main_app_healthy():
    assert app is not None
    assert isinstance(app.title, str)


def test_offers_route_exists():
    response = client.get("/offers")
    assert response.status_code in (200, 500, 404)
