"""POPIA-safe telemetry service with graceful no-op behavior."""
from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.degraded_mode import get_runtime_capabilities
try:
    from app.core.logging import get_logger
except ModuleNotFoundError:  # pragma: no cover - lightweight validation environments
    import logging

    def get_logger(name: str):
        return logging.getLogger(name)

log = get_logger(__name__)

ALLOWED_ANALYTICS_PROPERTIES = {
    "path",
    "grade_band",
    "subject",
    "topic_ref",
    "activity_type",
    "attempt_number",
    "correctness",
    "time_spent_seconds",
    "hint_used",
    "confidence",
    "gap_ratio",
    "feature",
    "variant",
}


class TelemetryService:
    """Dispatch analytics only when configured; otherwise log a safe local event."""

    async def track_event_async(self, event_name: str, pseudonym_id: str, properties: dict[str, Any] | None = None) -> None:
        payload = validate_event_payload(event_name, pseudonym_id, properties or {})
        capability = get_runtime_capabilities()["analytics"]
        if capability.status != "available":
            log.info("telemetry_noop", event_name=event_name, distinct_id=pseudonym_id, reason=capability.reason)
            return
        try:
            import posthog  # type: ignore

            posthog.project_api_key = settings.POSTHOG_API_KEY
            posthog.host = settings.POSTHOG_HOST
            posthog.capture(payload["distinct_id"], payload["event"], payload["properties"])
        except Exception as exc:  # noqa: BLE001 - telemetry must never break learner flows
            log.warning("telemetry_dispatch_failed", event_name=event_name, error=exc.__class__.__name__)

    @staticmethod
    def sanitize_properties(properties: dict[str, Any]) -> dict[str, Any]:
        """Return a sanitized subset of properties safe for analytics dispatch.

        Kept for backward compatibility with older tests and callers.
        """
        return {k: v for k, v in properties.items() if k in ALLOWED_ANALYTICS_PROPERTIES}


def validate_event_payload(event_name: str, pseudonym_id: str, properties: dict[str, Any]) -> dict[str, Any]:
    if not event_name or not event_name.replace("_", "").isalnum():
        raise ValueError("event_name must be snake_case alphanumeric")
    if "@" in pseudonym_id or len(pseudonym_id) > 128:
        raise ValueError("distinct_id must be pseudonymous and non-identifying")
    filtered = {key: value for key, value in properties.items() if key in ALLOWED_ANALYTICS_PROPERTIES}
    return {"event": event_name, "distinct_id": pseudonym_id or "anonymous", "properties": filtered}
