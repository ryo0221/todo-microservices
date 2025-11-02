from typing import Optional
from urllib import request
from urllib.parse import urljoin

import asyncio
from httpx import AsyncClient, Request, Response
from fastapi import Request as FastAPIRequest
from starlette.responses import JSONResponse


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
    path_and_query = request.url.path
    if request.url.query:
        path_and_query += f"?{request.url.query}"

    upstream_url = urljoin(upstream_base.rstrip("/") + "/", path_and_query.lstrip("/"))

    # 必要に応じてヘッダ転送を拡張
    headers = {}
    body = await request.body()
    req = Request(request.method, upstream_url, content=body, headers=headers)

    async with make_client() as client:
        # send() を使うことでテストの monkeypatch 対象に一致させる
        resp = await client.send(req)

    data = await _maybe_await_json(resp)
    return JSONResponse(content=data, status_code=getattr(resp, "status_code", 200))