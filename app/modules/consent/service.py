"""
EduBoost V2 — Consent Service (POPIA Gate)
require_active_consent() MUST be called at every learner endpoint.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.repositories import ConsentRepository


class ConsentService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = ConsentRepository(db)

    async def require_active_consent(self, learner_id: str) -> None:
        """Raise 403 if no active, non-expired parental consent exists."""
        consent = await self._repo.get_active(learner_id)
        if consent is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active parental consent required. Please contact your guardian.",
            )

    async def grant(self, guardian_id: str, learner_id: str, policy_version: str, ip_hash: str | None = None):
        return await self._repo.create(
            guardian_id=guardian_id,
            learner_id=learner_id,
            policy_version=policy_version,
            ip_address_hash=ip_hash,
        )

    async def revoke(self, learner_id: str) -> None:
        consent = await self._repo.get_active(learner_id)
        if consent:
            await self._repo.revoke(consent.id)

    async def get_status(self, learner_id: str):
        return await self._repo.get_active(learner_id)
