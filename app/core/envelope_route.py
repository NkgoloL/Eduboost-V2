"""
app/core/envelope_route.py
--------------------------
Provides ``EnvelopedRoute``, a custom ``APIRoute`` subclass that automatically
wraps any bare (non-enveloped) ``JSONResponse`` in the canonical
``ApiEnvelope`` format.

Usage — apply per-router (preferred, gives correct OpenAPI response_model):

    from fastapi import APIRouter
    from app.core.envelope_route import EnvelopedRoute

    router = APIRouter(route_class=EnvelopedRoute)

When ``route_class=EnvelopedRoute`` is set on a router, every endpoint that
returns a ``JSONResponse`` whose body is **not already an envelope** will be
wrapped transparently. This allows incremental migration: endpoints that
already call ``ok()`` / ``fail()`` / ``paginated()`` directly are unaffected
(the wrapper detects the envelope structure and passes them through).

Design notes
------------
* Request-ID is read from ``request.state.request_id`` (set by the request-ID
  middleware upstream) and injected into the envelope ``meta`` field.
* The ``api_version`` field is always ``"v2"``.
* HTTP status codes are preserved.
* Only ``JSONResponse`` bodies are touched; ``StreamingResponse`` and others
  are passed through unchanged.
* The wrapper never swallows exceptions — errors still propagate to
  ``app/core/exceptions.py`` handlers.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

API_VERSION = "v2"

# Keys present when a response is already wrapped in ApiEnvelope.
_ENVELOPE_KEYS = frozenset({"data", "error", "meta"})


def _is_already_enveloped(body: Any) -> bool:
    """Return True if *body* already looks like an ApiEnvelope payload."""
    if not isinstance(body, dict):
        return False
    return _ENVELOPE_KEYS.issubset(body.keys())


def _wrap(body: Any, request_id: str | None, status_code: int) -> dict:
    """Wrap *body* in the canonical ApiEnvelope structure."""
    return {
        "data": body,
        "error": None,
        "meta": {
            "api_version": API_VERSION,
            "request_id": request_id or "",
        },
    }


class EnvelopedRoute(APIRoute):
    """
    Custom route class that wraps bare JSON responses in ``ApiEnvelope``.

    Set on an ``APIRouter`` via ``route_class=EnvelopedRoute``.  Endpoints
    that already return a fully-formed envelope are passed through unchanged.
    """

    def get_route_handler(self) -> Callable:
        original_handler = super().get_route_handler()

        async def enveloped_handler(request: Request) -> Response:
            response: Response = await original_handler(request)

            if not isinstance(response, JSONResponse):
                return response  # StreamingResponse, FileResponse, etc.

            try:
                body = json.loads(response.body)
            except (json.JSONDecodeError, ValueError):
                return response  # non-JSON body; pass through

            if _is_already_enveloped(body):
                return response  # already wrapped by ok() / fail() / paginated()

            request_id: str | None = getattr(
                getattr(request, "state", None), "request_id", None
            )

            wrapped = _wrap(body, request_id, response.status_code)
            return JSONResponse(
                content=wrapped,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        return enveloped_handler
