from httpx import AsyncClient, Request, Response
from fastapi import Request as FastAPIRequest
from starlette.responses import JSONResponse, Response as StarletteResponse


def make_client() -> AsyncClient:
    return AsyncClient()

async def _maybe_await_json(resp: Response):
    """
    テストの FakeResponse が `async def json()` を持つ想定に合わせて、
    実オブジェクト(httpx.Response)の `.json()` (同期) も扱えるようにする。
    """
    json_attr = getattr(resp, "json", None)
    if json_attr is None:
        return None
    try:
        # FakeResponse: async def json()
        return await json_attr()
    except TypeError:
        # httpx.Response: def json(self)
        return json_attr()


async def forward(request: FastAPIRequest, upstream_base: str) -> JSONResponse:
    """
    受け取ったリクエストを upstream に転送する最小実装。
    今はテスト簡便化のため body/headers は最小限。必要に応じて拡張。
    """
    # 元のパス＋クエリをそのまま連結
    path = request.url.path
    query = request.url.query
    base = upstream_base.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    upstream_url = base + path + (f"?{query}" if query else "")

    # ✅ ヘッダ転送：Authorization / X-Request-ID など
    forward_headers = {}
    for name, value in request.headers.items():
        lname = name.lower()
        if lname in ("authorization", "x-request-id"):
            forward_headers[name] = value

    # ボディ（今はそのまま）
    body = await request.body()
    req = Request(request.method, upstream_url, content=body, headers=forward_headers)
    async with make_client() as client:
        # send() を使うことでテストの monkeypatch 対象に一致させる
        resp = await client.send(req)

    # 下流へ転送
    async with make_client() as client:
        resp = await client.send(req)
    
    # レスポンス処理
    data = await _maybe_await_json(resp)
    status = getattr(resp, "status_code", 200)
    headers = getattr(resp, "headers", {})

    if isinstance(data, (dict, list, str, int, float)) or data is None:
        # JSON として返せる場合は JSONResponse
        return JSONResponse(
            content=data, 
            status_code=status,
            headers=headers
            )
    else:
        # それ以外（bytes など）はそのままバイナリでパススルー
        content = getattr(resp, "content", b"")
        media_type = None
        headers_obj = getattr(resp, "headers", None)
        if headers_obj:
            media_type = headers_obj.get("content-type")
        return StarletteResponse(
            content=content,
            status_code=status,
            media_type=media_type,
            headers=headers
        )