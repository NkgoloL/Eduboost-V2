"""
EduBoost SA — Consent Module
POPIA parental consent lifecycle management.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, write_audit_event
from app.core.exceptions import AuthorisationError, ConsentRequiredError
from app.core.metrics import consent_events_total
from app.models import ParentalConsent
from app.repositories import ConsentRepository, LearnerRepository

_consent_repo = ConsentRepository()
_learner_repo = LearnerRepository()


class ConsentService:

    async def grant_consent(
        self,
        learner_id: UUID,
        guardian_id: UUID,
        db: AsyncSession,
        *,
        request: Request | None = None,
        consent_version: str = "1.0",
    ) -> ParentalConsent:
        """
        Grant parental consent for a learner.
        Atomic: revokes existing consent and writes audit event in same transaction.
        """
        learner = await _learner_repo.get_or_404(learner_id, db)
        if learner.guardian_id != guardian_id:
            raise AuthorisationError("You are not the guardian of this learner")

        consent = await _consent_repo.grant(
            learner_id, guardian_id, db,
            ip_address=_get_ip(request),
            user_agent=_get_ua(request),
            consent_version=consent_version,
        )

        await write_audit_event(
            db,
            action=AuditAction.CONSENT_GRANTED,
            actor_id=guardian_id,
            learner_id=learner_id,
            resource_type="parental_consent",
            resource_id=str(consent.id),
            ip_address=_get_ip(request),
        )
        consent_events_total.labels(event="granted").inc()
        return consent

    async def revoke_consent(
        self,
        learner_id: UUID,
        guardian_id: UUID,
        db: AsyncSession,
        *,
        reason: str = "guardian_request",
        request: Request | None = None,
    ) -> int:
        """
        Revoke parental consent. Returns count of consents revoked.
        Audit event committed in same transaction.
        """
        learner = await _learner_repo.get_or_404(learner_id, db)
        if learner.guardian_id != guardian_id:
            raise AuthorisationError("You are not the guardian of this learner")

        count = await _consent_repo.revoke(learner_id, db, reason=reason)

        await write_audit_event(
            db,
            action=AuditAction.CONSENT_REVOKED,
            actor_id=guardian_id,
            learner_id=learner_id,
            metadata={"reason": reason, "count_revoked": count},
            ip_address=_get_ip(request),
        )
        consent_events_total.labels(event="revoked").inc()
        return count

    async def require_active_consent(
        self, learner_id: UUID, db: AsyncSession
    ) -> ParentalConsent:
        """
        Assert active consent exists — raises ConsentRequiredError if not.
        Used by the FastAPI consent gate dependency.
        """
        consent = await _consent_repo.get_active(learner_id, db)
        if consent is None:
            raise ConsentRequiredError(
                "Active parental consent is required to access learner data."
            )
        return consent

    async def get_expiring_consents(
        self, db: AsyncSession, days: int = 30
    ) -> list[ParentalConsent]:
        """Used by the ARQ renewal reminder background job."""
        return await _consent_repo.get_expiring_soon(db, days=days)


def _get_ip(request: Request | None) -> str | None:
    if request is None:
        return None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _get_ua(request: Request | None) -> str | None:
    return request.headers.get("User-Agent") if request else None
