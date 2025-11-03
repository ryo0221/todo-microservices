from starlette.testclient import TestClient
from gateway.app.main import app

def test_cors_headers_present():
    """
    Gateway should add standard CORS headers to all responses.
    """
    client = TestClient(app)
    resp = client.options("/todos")  # Preflight
    print("CORS Preflight Response Headers:", resp.headers)
    # Preflight response must not require JSON decoding
    assert resp.status_code in (200, 204)
    headers = resp.headers
    assert headers.get("access-control-allow-origin") == "*"
    assert "access-control-allow-methods" in headers