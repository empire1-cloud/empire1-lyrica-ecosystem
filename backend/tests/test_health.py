"""Tests for the /api/health route."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.pop("MONGO_URL", None)
os.environ.pop("STRIPE_SECRET_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402

from server import app  # noqa: E402

client = TestClient(app)


def test_health_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["mongo_configured"] is False
    assert body["stripe_configured"] is False


def test_existing_root_route_untouched():
    """Guardrail: the pre-existing '/api/' route must keep working."""
    resp = client.get("/api/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}
