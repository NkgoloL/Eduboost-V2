"""
EduBoost SA — Middleware Stack
Request ID injection, timing headers, structured logging, rate limit headers.
"""
from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import http_request_duration_seconds, http_requests_total

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique X-Request-ID to every request and response."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)  # type: ignore[operator]
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Record request duration and emit Prometheus metrics."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)  # type: ignore[operator]
        duration = time.perf_counter() - start

        # Normalise path to avoid high-cardinality labels
        endpoint = _normalise_path(request.url.path)
        method = request.method
        status = str(response.status_code)

        http_requests_total.labels(method=method, endpoint=endpoint, status_code=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

        response.headers["X-Response-Time"] = f"{duration * 1000:.1f}ms"
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with structured fields (request_id, method, path, status, ms)."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)  # type: ignore[operator]
        duration_ms = (time.perf_counter() - start) * 1000
        request_id = getattr(request.state, "request_id", "-")

        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": _get_client_ip(request),
            },
        )
        return response


def _normalise_path(path: str) -> str:
    """Replace UUID segments with {id} to reduce Prometheus label cardinality."""
    import re
    path = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "{id}",
        path,
        flags=re.IGNORECASE,
    )
    return path


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
