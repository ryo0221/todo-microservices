from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.routes_auth import router as auth_router
from .models.user import Base
from .db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初期フェーズはマイグレーションなしでテーブル作成
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Auth Service", lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}
