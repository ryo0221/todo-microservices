import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_get_me_with_valid_token(monkeypatch):
    token = create_access_token("user@example.com")

    res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["user"] == "user@example.com"

def test_get_me_with_invalid_token():
    res = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401

def test_get_me_without_token():
    res = client.get("/auth/me")
    assert res.status_code == 401