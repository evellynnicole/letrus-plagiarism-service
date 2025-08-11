# tests/test_app.py
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_compare_endpoint():
    with patch("app.api.compare.CompareService") as MockCls:
        MockCls.return_value.compare.return_value = {
            "mode": "all",
            "matches": [{"similarity": 0.9, "text": "teste"}],
        }
        r = client.post("/compare", json={"text": "teste"})
        assert r.status_code == 200
        assert "mode" in r.json()


def test_compare_validation():
    r = client.post("/compare", json={"text": ""})
    assert r.status_code == 422
