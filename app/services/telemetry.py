"""POPIA-safe PostHog telemetry helpers for product analytics."""
from __future__ import annotations

import re
from typing import Any

import anyio
import posthog

from app.core.config import get_settings

settings = get_settings()
_EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")
_SA_ID_RE = re.compile(r"\b\d{13}\b")
_UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)
_PII_KEYS = {"email", "display_name", "name", "guardian_id", "learner_id", "user_id", "phone", "sa_id"}


class TelemetryService:
    """
    PostHog-based product analytics.
    Only tracks pseudonymous events with no PII.
    """

    def __init__(self) -> None:
        if settings.POSTHOG_API_KEY:
            posthog.api_key = settings.POSTHOG_API_KEY
            posthog.host = settings.POSTHOG_HOST
            self._enabled = True
        else:
            self._enabled = False

    @staticmethod
    def sanitize_properties(properties: dict[str, Any] | None) -> dict[str, Any]:
        sanitized: dict[str, Any] = {}
        for key, value in (properties or {}).items():
            if key.lower() in _PII_KEYS:
                continue
            if isinstance(value, str) and (
                _EMAIL_RE.search(value) or _SA_ID_RE.search(value) or _UUID_RE.search(value)
            ):
                continue
            sanitized[key] = value
        return sanitized

    def track_event(self, event_name: str, pseudonym_id: str, properties: dict[str, Any] | None = None) -> None:
        if not self._enabled:
            return

        posthog.capture(
            distinct_id=pseudonym_id,
            event=event_name,
            properties=self.sanitize_properties(properties),
        )

    async def track_event_async(
        self,
        event_name: str,
        pseudonym_id: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        if not self._enabled:
            return
        await anyio.to_thread.run_sync(self.track_event, event_name, pseudonym_id, properties)

    def identify_user(self, pseudonym_id: str, properties: dict[str, Any] | None = None) -> None:
        if not self._enabled:
            return

        posthog.identify(
            distinct_id=pseudonym_id,
            properties=self.sanitize_properties(properties),
        )
