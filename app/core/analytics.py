"""POPIA-safe analytics middleware.

Only pseudonymous learner identifiers are allowed as analytics user ids. This
module intentionally avoids names, emails, guardian ids, and raw UUID-bearing
request bodies.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.core.logging import get_logger

log = get_logger(__name__)

TRACKED_EVENTS = {
    "/api/v2/auth/login": "session_start",
    "/api/v2/diagnostics/submit": "diagnostic_completed",
    "/api/v2/lessons/": "lesson_generated",
    "/api/v2/study-plans": "study_plan_created",
    "/api/v2/consent/grant": "consent_granted",
    "/api/v2/consent/revoke": "consent_revoked",
}


async def analytics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    event_name = _event_for_path(request.url.path)
    if event_name and response.status_code < 400:
        pseudonym_id = request.headers.get("x-eduboost-pseudonym-id")
        payload = build_analytics_payload(event_name, pseudonym_id, request.url.path)
        log.info("analytics_event", **payload)
    return response


def build_analytics_payload(event_name: str, pseudonym_id: str | None, path: str) -> dict:
    return {
        "event": event_name,
        "user_id": pseudonym_id or "anonymous",
        "path": path,
    }


def _event_for_path(path: str) -> str | None:
    for prefix, event in TRACKED_EVENTS.items():
        if path.startswith(prefix):
            return event
    return None
