from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .proxy import forward
from .middleware.cors_preflight import PreflightMiddleware
from .middleware.logging_middleware import LoggingMiddleware

app = FastAPI(title="API Gateway")

# Register custom middleware first (intercepts before routing)
app.add_middleware(PreflightMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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