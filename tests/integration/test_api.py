import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAPIRoot:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "version" in response.json()

    def test_root_message(self, client):
        response = client.get("/")
        assert "TFT HUD API" in response.json()["message"]


class TestAPIHealth:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_ping(self, client):
        response = client.get("/api/ping")
        assert response.status_code == 200
        assert response.json()["pong"] is True


class TestAPICompositions:
    def test_comps_endpoint_exists(self, client):
        response = client.get("/api/comps")
        assert response.status_code == 200

    def test_comps_with_limit(self, client):
        response = client.get("/api/comps?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_comps_with_patch_filter(self, client):
        response = client.get("/api/comps?patch=14.1")
        assert response.status_code == 200

    def test_comps_with_tier_filter(self, client):
        response = client.get("/api/comps?tier=S")
        assert response.status_code == 200


class TestAPIPatch:
    def test_current_patch_endpoint(self, client):
        response = client.get("/api/patch/current")
        assert response.status_code in [200, 500]


class TestAPIDocs:
    def test_docs_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_available(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()
