"""
EduBoost V2 — PostHog Telemetry Service (Phase 5.1)

POPIA-safe analytics: Only pseudonymous learner IDs, no PII.
Tracks user engagement events for product analytics.

BOUNDARY: May import from /app/core/.
"""
from __future__ import annotations

import posthog
from posthog import Posthog

from app.core.config import get_settings

settings = get_settings()


class TelemetryService:
    """
    PostHog-based product analytics.
    Only tracks pseudonymous events with no PII.
    """

    def __init__(self) -> None:
        if settings.posthog_api_key:
            posthog.api_key = settings.posthog_api_key
            posthog.host = settings.posthog_host
            self._enabled = True
        else:
            self._enabled = False

    def track_event(
        self,
        event_name: str,
        pseudonym_id: str,
        properties: dict | None = None,
    ) -> None:
        """
        Track an analytics event.

        Args:
            event_name: The event name (e.g., 'lesson_generated')
            pseudonym_id: Pseudonymous learner ID (no PII)
            properties: Additional event properties
        """
        if not self._enabled:
            return

        posthog.capture(
            distinct_id=pseudonym_id,
            event=event_name,
            properties=properties or {},
        )

    def identify_user(self, pseudonym_id: str, properties: dict | None = None) -> None:
        """
        Set user properties for a pseudonymous user.

        Args:
            pseudonym_id: Pseudonymous learner ID
            properties: User properties (no PII)
        """
        if not self._enabled:
            return

        posthog.identify(
            distinct_id=pseudonym_id,
            properties=properties or {},
        )