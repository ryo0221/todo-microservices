from fastapi import FastAPI, Request
from .proxy import forward

app = FastAPI(title="API Gateway")

@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}

# ルーティング: prefixで振り分け（最小）
AUTH_BASE = "http://auth:8000"
TODO_BASE = "http://todo:8000"

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def auth_proxy(path: str, request: Request):
    return await forward(request, AUTH_BASE)

@app.api_route("/todos/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def todos_proxy(path: str, request: Request):
    return await forward(request, TODO_BASE)