from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.routes_todos import router as todos_router
from .models.todo import Base
from .db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Todo Service", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "service": "todo"}

app.include_router(todos_router)