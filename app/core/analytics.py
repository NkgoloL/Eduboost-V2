"""POPIA-safe analytics middleware."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.core.logging import get_logger
from app.services.telemetry import TelemetryService

log = get_logger(__name__)

TRACKED_EVENTS = {
    "/api/v2/auth/login": "session_start",
    "/api/v2/diagnostics/submit": "diagnostic_completed",
    "/api/v2/lessons/": "lesson_viewed",
    "/api/v2/study-plans": "study_plan_created",
    "/api/v2/consent/grant": "consent_granted",
    "/api/v2/consent/revoke": "consent_revoked",
}


async def analytics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    analytics_context = getattr(request.state, "analytics", None)
    if analytics_context and response.status_code < 400:
        event_name = analytics_context["event"]
        pseudonym_id = analytics_context["pseudonym_id"]
        payload = build_analytics_payload(
            event_name,
            pseudonym_id,
            request.url.path,
            analytics_context.get("properties"),
        )
        log.info("analytics_event", **payload)
        asyncio.create_task(
            TelemetryService().track_event_async(
                event_name,
                pseudonym_id,
                payload["properties"],
            )
        )
        return response

    event_name = _event_for_path(request.url.path)
    if event_name and response.status_code < 400:
        pseudonym_id = request.headers.get("x-eduboost-pseudonym-id") or "anonymous"
        payload = build_analytics_payload(event_name, pseudonym_id, request.url.path)
        log.info("analytics_event", **payload)
        asyncio.create_task(TelemetryService().track_event_async(event_name, pseudonym_id, payload["properties"]))
    return response


def build_analytics_payload(
    event_name: str,
    pseudonym_id: str | None,
    path: str,
    properties: dict | None = None,
) -> dict:
    return {
        "analytics_event": event_name,
        "distinct_id": pseudonym_id or "anonymous",
        "path": path,
        "properties": {"path": path, **(properties or {})},
    }


def _event_for_path(path: str) -> str | None:
    for prefix, event in TRACKED_EVENTS.items():
        if path.startswith(prefix):
            return event
    return None
