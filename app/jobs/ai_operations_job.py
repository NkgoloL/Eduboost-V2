"""Durable Phase 6 maintenance jobs for AI operations accounting."""
from __future__ import annotations

from app.core.database import AsyncSessionLocal
from app.services.ai_operations import AIOperationsService


async def expire_ai_usage_reservations(ctx: dict | None = None) -> dict[str, int]:
    async with AsyncSessionLocal() as db:
        expired = await AIOperationsService(db).expire_stale()
        await db.commit()
        return {"expired_reservations": expired}
