"""API Deprecation and Canonical Versioning Middleware (TSR-10).

Ensures `/api/v2` is the canonical routing authority. Requests arriving at
legacy `/v2/*` routes receive HTTP Deprecation and Sunset headers pointing
to the canonical `/api/v2` path.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

SUNSET_DATE = "Sun, 01 Nov 2026 00:00:00 GMT"


class APIDeprecationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        path = request.url.path

        # If a request enters via legacy /v2 path, inject deprecation headers
        if path.startswith("/v2/") or path == "/v2":
            canonical_path = path.replace("/v2", "/api/v2", 1)
            response.headers["Deprecation"] = "@1793491200"  # Nov 1 2026 timestamp
            response.headers["Sunset"] = SUNSET_DATE
            response.headers["Link"] = f'<{canonical_path}>; rel="canonical"'
            response.headers["X-API-Canonical-Prefix"] = "/api/v2"

        return response

