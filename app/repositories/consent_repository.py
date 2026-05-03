"""Parental consent persistence repository for EduBoost V2."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import ParentalConsent


class ConsentRepository(BaseRepository[ParentalConsent]):
    model = ParentalConsent

    async def get_active(self, learner_id: UUID, db: AsyncSession) -> ParentalConsent | None:
        result = await db.execute(
            select(ParentalConsent)
            .where(ParentalConsent.learner_id == learner_id)
            .where(ParentalConsent.is_active.is_(True))
            .where(ParentalConsent.expires_at > datetime.now(UTC))
            .order_by(ParentalConsent.granted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def grant(
        self,
        learner_id: UUID,
        guardian_id: UUID,
        db: AsyncSession,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
        consent_version: str = "1.0",
    ) -> ParentalConsent:
        await self.revoke(learner_id, db, reason="superseded")
        return await self.create(
            db,
            learner_id=learner_id,
            guardian_id=guardian_id,
            is_active=True,
            granted_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=365),
            consent_version=consent_version,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def revoke(self, learner_id: UUID, db: AsyncSession, *, reason: str) -> int:
        result = await db.execute(
            select(ParentalConsent)
            .where(ParentalConsent.learner_id == learner_id)
            .where(ParentalConsent.is_active.is_(True))
        )
        consents = list(result.scalars().all())
        for consent in consents:
            consent.is_active = False
            consent.revoked_at = datetime.now(UTC)
            consent.revocation_reason = reason
            db.add(consent)
        await db.flush()
        return len(consents)

    async def get_expiring_soon(self, db: AsyncSession, *, days: int = 30) -> list[ParentalConsent]:
        now = datetime.now(UTC)
        result = await db.execute(
            select(ParentalConsent)
            .where(ParentalConsent.is_active.is_(True))
            .where(ParentalConsent.expires_at > now)
            .where(ParentalConsent.expires_at <= now + timedelta(days=days))
            .order_by(ParentalConsent.expires_at.asc())
        )
        return list(result.scalars().all())
