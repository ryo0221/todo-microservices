import time
from app.core.security import create_access_token, create_refresh_token
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_refresh_with_valid_token():
    refresh = create_refresh_token("user@example.com")
    res = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_refresh_with_invalid_token():
    res = client.post("/auth/refresh", json={"refresh_token": "invalid"})
    assert res.status_code == 401


def test_refresh_with_expired_token():
    short_refresh = create_refresh_token("user@example.com", expires_days=0)
    time.sleep(1)
    res = client.post("/auth/refresh", json={"refresh_token": short_refresh})
    assert res.status_code == 401
