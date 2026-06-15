"""Phase 7 scheduled curriculum coverage snapshots."""
from __future__ import annotations

import os

from app.core.database import AsyncSessionLocal
from app.services.content_scope_registry import ContentScopeRegistry
from app.services.curriculum_expansion import CurriculumExpansionService


async def capture_weekly_curriculum_coverage(ctx: dict | None = None) -> dict[str, int]:
    registry = ContentScopeRegistry()
    source_commit_sha = os.getenv("GIT_COMMIT_SHA")
    async with AsyncSessionLocal() as db:
        service = CurriculumExpansionService(db, registry=registry)
        count = 0
        for scope in registry.list_active_scopes():
            await service.capture_snapshot(scope.scope_id, source_commit_sha)
            count += 1
        await db.commit()
        return {"snapshots_created": count}
