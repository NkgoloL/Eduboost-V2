from __future__ import annotations

from app.core.config import settings


class SystemServiceV2:
    async def health(self) -> dict:
        return {"status": "ok", "version": settings.APP_VERSION, "mode": "v2-baseline"}

    async def pillars(self) -> dict:
        return {
            "architecture": "modular-monolith",
            "audit_target": "postgresql-append-only",
            "pillars": [
                "diagnostic-engine",
                "lesson-generator",
                "policy-enforcement",
                "audit",
                "learner-archetype",
            ]
        }

    async def schema_status(self) -> dict:
        return {"status": "ok", "schema": "v2"}
