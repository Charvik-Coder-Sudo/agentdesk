"""FR-003: the health endpoint."""

from app import __version__


def test_health_returns_status_version_and_uptime(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == __version__ == "0.1.0"
    assert isinstance(data["uptime"], (int, float)) and data["uptime"] >= 0


def test_health_needs_no_csrf_token(client):
    # A plain GET without any token or session works.
    assert client.get("/api/v1/health", headers={}).status_code == 200
