import pytest
from httpx import AsyncClient, ASGITransport
from gateway.app.main import app


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.status_code = status_code
        self._payload = payload

    async def json(self):
        return self._payload


class FakeClient:
    """
    httpx.AsyncClient 互換の最小モック。
    - async with ...: OK
    - send(self, request, **kwargs): OK
    """
    def __init__(self, label):
        self.label = label  # "auth-ok" / "todo-ok"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def send(self, request, **kwargs):
        # request は httpx.Request
        return FakeResponse({"mock": self.label, "path": request.url.path})


@pytest.mark.asyncio
async def test_forward_auth_routes(monkeypatch):
    # make_client() を FakeClient に差し替える（引数は不要）
    monkeypatch.setattr("gateway.app.proxy.make_client", lambda: FakeClient("auth-ok"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/auth/test")

    assert resp.status_code == 200
    assert resp.json() == {"mock": "auth-ok", "path": "/auth/test"}


@pytest.mark.asyncio
async def test_forward_todo_routes(monkeypatch):
    monkeypatch.setattr("gateway.app.proxy.make_client", lambda: FakeClient("todo-ok"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/todos/abc")

    assert resp.status_code == 200
    assert resp.json() == {"mock": "todo-ok", "path": "/todos/abc"}

@pytest.mark.asyncio
async def test_forward_query_params(monkeypatch):
    # 偽クライアント：受け取った URL を確認したい
    class QueryCheckClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def send(self, request, **kwargs):
            # クエリが保持されているか確認
            class FakeResponse:
                status_code = 200
                async def json(inner_self):
                    return {
                        "path": request.url.path,
                        "query": request.url.query.decode("utf-8") if isinstance(request.url.query, (bytes, bytearray)) else request.url.query
                    }
            return FakeResponse()

    monkeypatch.setattr("gateway.app.proxy.make_client", lambda: QueryCheckClient())

    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/todos/search?q=openai&page=2")

    assert resp.status_code == 200
    assert resp.json() == {
        "path": "/todos/search",
        "query": "q=openai&page=2"
    }

@pytest.mark.asyncio
async def test_forward_headers(monkeypatch):
    """Authorizationヘッダなどが下流へ転送されることを確認"""

    class HeaderCheckClient:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        async def send(self, request, **kwargs):
            # 下流で受け取ったヘッダを確認できるように返す
            class FakeResponse:
                status_code = 200
                async def json(inner_self):
                    # Authorizationなど特定のヘッダを抽出
                    return {
                        "headers": {
                            "authorization": request.headers.get("authorization"),
                            "x-request-id": request.headers.get("x-request-id"),
                        }
                    }
            return FakeResponse()

    monkeypatch.setattr("gateway.app.proxy.make_client", lambda: HeaderCheckClient())

    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {
            "Authorization": "Bearer testtoken123",
            "X-Request-ID": "req-999",
        }
        resp = await ac.get("/todos/abc", headers=headers)

    assert resp.status_code == 200
    assert resp.json() == {
        "headers": {
            "authorization": "Bearer testtoken123",
            "x-request-id": "req-999",
        }
    }