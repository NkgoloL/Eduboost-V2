"""Parental consent persistence repository for EduBoost V2."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import ParentalConsent


class ConsentRepository(BaseRepository[ParentalConsent]):
    model = ParentalConsent

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db

    def _db(self, db: AsyncSession | None) -> AsyncSession:
        session = db or self.db
        if session is None:
            raise ValueError("ConsentRepository requires an AsyncSession")
        return session

    async def get_active(self, learner_id: str, db: AsyncSession | None = None) -> ParentalConsent | None:
        db = self._db(db)
        result = await db.execute(
            select(ParentalConsent)
            .where(ParentalConsent.learner_id == learner_id)
            .where(ParentalConsent.revoked_at.is_(None))
            .where(ParentalConsent.expires_at > datetime.now(UTC))
            .order_by(ParentalConsent.granted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def grant(
        self,
        learner_id: str,
        guardian_id: str,
        db: AsyncSession | None = None,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
        consent_version: str = "1.0",
    ) -> ParentalConsent:
        db = self._db(db)
        # AuditLog emission happens in ConsentService; this repository only
        # performs persistence updates.
        existing = await self._get_latest_for_pair(learner_id, guardian_id, db)
        now = datetime.now(UTC)
        if existing is None:
            return await self.create(
                db,
                learner_id=learner_id,
                guardian_id=guardian_id,
                granted_at=now,
                expires_at=now + timedelta(days=365),
                policy_version=consent_version,
                ip_address_hash=ip_address,
            )
        existing.granted_at = now
        existing.expires_at = now + timedelta(days=365)
        existing.policy_version = consent_version
        existing.revoked_at = None
        existing.ip_address_hash = ip_address
        db.add(existing)
        await db.flush()
        return existing

    async def revoke(
        self,
        learner_id: str,
        db: AsyncSession | None = None,
        *,
        reason: str,
    ) -> int:
        db = self._db(db)
        # AuditLog emission happens in ConsentService; this repository only
        # performs persistence updates.
        result = await db.execute(
            select(ParentalConsent)
            .where(ParentalConsent.learner_id == learner_id)
            .where(ParentalConsent.revoked_at.is_(None))
        )
        consents = list(result.scalars().all())
        for consent in consents:
            consent.revoked_at = datetime.now(UTC)
            db.add(consent)
        await db.flush()
        return len(consents)

    async def renew(
        self,
        learner_id: str,
        guardian_id: str,
        consent_version: str,
        db: AsyncSession | None = None,
    ) -> tuple[ParentalConsent | None, ParentalConsent]:
        db = self._db(db)
        # AuditLog emission happens in ConsentService; this repository only
        # performs persistence updates.
        previous = await self.get_active(learner_id, db)
        renewed = await self.grant(
            learner_id=learner_id,
            guardian_id=guardian_id,
            db=db,
            consent_version=consent_version,
        )
        return previous, renewed

    async def get_expiring_soon(self, db: AsyncSession | None = None, *, days: int = 30) -> list[ParentalConsent]:
        db = self._db(db)
        now = datetime.now(UTC)
        result = await db.execute(
            select(ParentalConsent)
            .where(ParentalConsent.revoked_at.is_(None))
            .where(ParentalConsent.expires_at > now)
            .where(ParentalConsent.expires_at <= now + timedelta(days=days))
            .order_by(ParentalConsent.expires_at.asc())
        )
        return list(result.scalars().all())

    async def _get_latest_for_pair(
        self,
        learner_id: str,
        guardian_id: str,
        db: AsyncSession,
    ) -> ParentalConsent | None:
        result = await db.execute(
            select(ParentalConsent)
            .where(ParentalConsent.learner_id == learner_id)
            .where(ParentalConsent.guardian_id == guardian_id)
            .order_by(ParentalConsent.granted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
