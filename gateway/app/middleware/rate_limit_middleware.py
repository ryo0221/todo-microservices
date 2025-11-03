from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from gateway.app.core.rate_limiter import InMemoryRateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware wrapper around a RateLimiter.
    """

    def __init__(self, app, limit: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = InMemoryRateLimiter(limit=limit, window_seconds=window_seconds)

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        if not self.limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )

        response = await call_next(request)
        return response
