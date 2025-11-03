import pytest
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from gateway.app.middleware.rate_limit_middleware import RateLimitMiddleware


@pytest.fixture()
def limited_app():
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, limit=3, window_seconds=2)

    @app.get("/ping")
    async def ping():
        return JSONResponse({"message": "pong"})

    return app


def test_rate_limit_blocks_after_limit_exceeded(limited_app):
    """
    RateLimitMiddleware should allow up to N requests in the window,
    then return 429 Too Many Requests for subsequent ones.
    """
    client = TestClient(limited_app)

    # Make 3 allowed requests
    for _ in range(3):
        r = client.get("/ping")
        assert r.status_code == 200

    # 4th should be blocked
    r = client.get("/ping")
    assert r.status_code == 429
    assert r.json()["detail"] == "Rate limit exceeded"

    # After window resets, it should allow again
    import time
    time.sleep(2.1)
    r2 = client.get("/ping")
    assert r2.status_code == 200