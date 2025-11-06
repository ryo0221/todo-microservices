from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class PreflightMiddleware(BaseHTTPMiddleware):
    """
    Handle CORS preflight requests (OPTIONS) globally before hitting routes.
    Ensures consistent behavior even when FastAPI doesn't register the method.
    """

    async def dispatch(self, request, call_next):
        # Catch CORS preflight early
        if request.method == "OPTIONS":
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                },
            )
        return await call_next(request)
