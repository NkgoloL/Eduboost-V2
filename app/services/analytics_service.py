"""V2 Analytics service for telemetry hooks (PostHog/Lightweight)."""

from __future__ import annotations

from typing import Any

from app.core.config import get_v2_settings
from app.services.audit_service import AuditService


class AnalyticsService:
    """Manages telemetry and product-loop tracking."""

    def __init__(self) -> None:
        self.settings = get_v2_settings()
        self.audit = AuditService()
        # In a real app, you'd init the PostHog client here:
        # self.posthog = Posthog(project_api_key=self.settings.posthog_api_key)
        self.posthog_active = False # Simplified for baseline

    async def track_event(
        self, 
        event_name: str, 
        distinct_id: str, 
        properties: dict[str, Any] | None = None
    ) -> None:
        """Send an event to the analytics platform (telemetry hook)."""
        # Always mirror to local audit for POPIA traceability
        await self.audit.log_event(
            event_type=f"ANALYTICS_{event_name.upper()}",
            learner_id=distinct_id if "-" in distinct_id else None,
            payload=properties or {},
        )

        if self.posthog_active:
            # self.posthog.capture(distinct_id, event_name, properties)
            pass

    async def track_lesson_completion(self, learner_id: str, lesson_id: str, duration_seconds: int) -> None:
        await self.track_event(
            "lesson_completed", 
            learner_id, 
            {"lesson_id": lesson_id, "duration": duration_seconds}
        )

    async def track_diagnostic_start(self, learner_id: str, subject: str) -> None:
        await self.track_event("diagnostic_started", learner_id, {"subject": subject})
