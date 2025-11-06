from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .cors_preflight import PreflightMiddleware
from .logging_middleware import LoggingMiddleware
from .rate_limit_middleware import RateLimitMiddleware


def register_middlewares(app: FastAPI) -> None:
    """
    Register all cross-cutting middlewares in a unified, ordered way.
    Order matters:
        1. CORSPreflightMiddleware — handle OPTIONS early
        2. RateLimitMiddleware — limit before heavy processing
        3. LoggingMiddleware — log everything including 429s
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(PreflightMiddleware)
    app.add_middleware(RateLimitMiddleware, limit=10, window_seconds=60)
    app.add_middleware(LoggingMiddleware)
