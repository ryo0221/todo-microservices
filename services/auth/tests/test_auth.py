import jwt
from app.core.settings import settings


def test_register_returns_token_and_creates_user(client):
    r = client.post(
        "/auth/register", json={"email": "alice@example.com", "password": "password123"}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["token_type"] == "bearer"
    token = body["access_token"]
    decoded = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["typ"] == "access"
    assert "sub" in decoded  # user id


def test_register_conflict_on_duplicate_email(client):
    payload = {"email": "bob@example.com", "password": "password123"}
    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 409
    assert r2.json()["detail"] == "email already registered"


def test_login_success_and_invalid_credentials(client):
    # arrange: create user via register
    client.post(
        "/auth/register", json={"email": "carol@example.com", "password": "passpass88"}
    )

    # act: good login
    ok = client.post(
        "/auth/login", json={"email": "carol@example.com", "password": "passpass88"}
    )
    assert ok.status_code == 200
    assert "access_token" in ok.json()

    # act: wrong password
    bad = client.post(
        "/auth/login", json={"email": "carol@example.com", "password": "WRONG"}
    )
    assert bad.status_code == 401
    assert bad.json()["detail"] == "invalid credentials"


def test_token_has_exp_claim(client):
    r = client.post(
        "/auth/register", json={"email": "dave@example.com", "password": "password123"}
    )
    token = r.json()["access_token"]
    decoded = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    assert "exp" in decoded
