import time
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)


def test_create_and_verify_access_token():
    token = create_access_token("user@example.com", expires_minutes=1)
    payload = verify_token(token, "access")

    assert payload is not None
    assert payload["sub"] == "user@example.com"
    assert payload["typ"] == "access"
    assert "exp" in payload


def test_create_and_verify_refresh_token():
    token = create_refresh_token("user@example.com")
    payload = verify_token(token, "refresh")

    assert payload is not None
    assert payload["typ"] == "refresh"
    assert payload["sub"] == "user@example.com"


def test_invalid_token_type_returns_none():
    access_token = create_access_token("user@example.com")
    # refresh として検証 → type mismatch なので None になるはず
    result = verify_token(access_token, "refresh")
    assert result is None


def test_expired_token_is_invalid():
    # 有効期限を「すぐに切れる」にして検証
    token = create_access_token("user@example.com", expires_minutes=0)
    time.sleep(1)  # 念のため待つ
    result = verify_token(token, "access")
    assert result is None
