import json
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("gateway")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs each request and response as structured JSON (method, path, status_code, duration_ms).
    """

    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as exc:
            status = 500
            raise exc
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            log_entry = {
                "method": request.method,
                "path": request.url.path,
                "status_code": status,
                "duration_ms": round(duration_ms, 2),
            }
            logger.info(json.dumps(log_entry))

        return response
