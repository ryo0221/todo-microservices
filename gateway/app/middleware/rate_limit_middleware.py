import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter middleware.
    Allows up to `limit` requests per `window_seconds` for each client IP.
    """

    def __init__(self, app, limit: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests = {}  # {client_ip: [timestamps]}

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        # Remove old requests
        timestamps = self._requests.get(client_ip, [])
        timestamps = [t for t in timestamps if now - t < self.window_seconds]

        # Update and check
        if len(timestamps) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )

        timestamps.append(now)
        self._requests[client_ip] = timestamps

        # Continue
        response = await call_next(request)
        return response
