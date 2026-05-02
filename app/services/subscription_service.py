"""Subscription tier orchestration for Free/Premium billing."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import cache_delete
from app.repositories.repositories import GuardianRepository


class SubscriptionService:
    def __init__(self, db: AsyncSession) -> None:
        self.guardians = GuardianRepository(db)

    async def activate_premium(self, guardian_id: str, stripe_subscription_id: str | None = None) -> None:
        await self.guardians.update_subscription(guardian_id, "premium", stripe_subscription_id)
        await self.reset_ai_quota(guardian_id)

    async def downgrade_to_free(self, guardian_id: str) -> None:
        await self.guardians.update_subscription(guardian_id, "free", None)

    async def reset_ai_quota(self, guardian_id: str) -> None:
        await cache_delete(f"ai_quota:{guardian_id}")
