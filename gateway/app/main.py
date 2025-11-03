from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from .graphql.schema import schema
from .proxy import forward
from .middleware import register_middlewares

app = FastAPI(title="API Gateway")

app.include_router(GraphQLRouter(schema=schema), prefix="/graphql")

register_middlewares(app)

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