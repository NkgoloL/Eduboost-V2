"""Stripe webhook event idempotency repository for EduBoost V2."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import StripeWebhookEvent


class StripeEventRepository(BaseRepository[StripeWebhookEvent]):
    model = StripeWebhookEvent

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    async def exists(self, db: AsyncSession, stripe_event_id: str) -> bool:
        """Check if a Stripe event ID has already been processed."""
        stmt = select(StripeWebhookEvent).where(StripeWebhookEvent.stripe_event_id == stripe_event_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def is_processed(self, stripe_event_id: str) -> bool:
        """Compatibility alias for exists(). Note: requires self.db to be set or use exists(db, ...)"""
        if not hasattr(self, "db") or self.db is None:
            raise ValueError("is_processed requires a bound session. Use exists(db, ...) instead.")
        return await self.exists(self.db, stripe_event_id)

    async def record_event(
        self,
        db: AsyncSession,
        stripe_event_id: str,
        event_type: str,
        payload: dict,
    ) -> StripeWebhookEvent:
        """Log a processed Stripe event for idempotency."""
        return await self.create(
            db,
            stripe_event_id=stripe_event_id,
            event_type=event_type,
            payload=payload,
        )

    async def record(self, stripe_event_id: str, event_type: str, payload: dict) -> StripeWebhookEvent:
        """Compatibility alias for record_event()."""
        if not hasattr(self, "db") or self.db is None:
            raise ValueError("record requires a bound session. Use record_event(db, ...) instead.")
        return await self.record_event(self.db, stripe_event_id, event_type, payload)
