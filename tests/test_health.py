from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


def test_health_ok():
    # Build a fresh app instance — the factory pattern makes this trivial.
    get_settings.cache_clear()
    settings = get_settings()
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": settings.PROJECT_NAME,
    }
