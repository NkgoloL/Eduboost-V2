"""Consent-gated diagnostic session orchestration.

Provides a :class:`ConsentService` used by diagnostic flows to enforce
active parental consent before learner assessment data can be accessed
or generated.  Every consent state change is committed in the same
transaction as the corresponding audit event.

This module is distinct from :mod:`app.modules.consent.service` — it
focuses on diagnostic-flow consent checks and is co-located with the
IRT engine for import convenience.
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
    """Parental consent checks for diagnostic flows.

    Used by the :class:`~app.modules.diagnostics.irt_engine.DiagnosticEngine`
    and diagnostic API routes to ensure active parental consent before a
    learner's assessment or data is accessed.

    All operations are audit-logged via
    :func:`~app.core.audit.write_audit_event`.

    Example:
        ::

            svc = ConsentService()
            consent = await svc.require_active_consent(learner_id, db)
    """

    async def grant_consent(
        self,
        learner_id: UUID,
        guardian_id: UUID,
        db: AsyncSession,
        *,
        request: Request | None = None,
        consent_version: str = "1.0",
    ) -> ParentalConsent:
        """Grant parental consent for a learner.

        Atomic operation: revokes any existing consent, creates a new
        :class:`~app.models.ParentalConsent` record, and writes an
        audit event in the same database transaction.

        Args:
            learner_id: UUID of the learner being covered.
            guardian_id: UUID of the parent granting consent.
            db: Async database session.
            request: Optional FastAPI request for IP / user-agent extraction.
            consent_version: Policy version the guardian agreed to
                (default ``"1.0"``).

        Returns:
            ParentalConsent: The newly created consent record.

        Raises:
            AuthorisationError: When the guardian is not the parent of
                the specified learner.

        Example:
            ::

                consent = await svc.grant_consent(
                    learner_id, guardian_id, db, consent_version="1.2",
                )
                assert consent.is_active
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
        """Revoke parental consent for a learner.

        Sets consent status to revoked and records a
        :attr:`~app.core.audit.AuditAction.CONSENT_REVOKED` audit event
        in the same transaction.

        Args:
            learner_id: UUID of the learner whose consent is revoked.
            guardian_id: UUID of the guardian performing the revocation.
            db: Async database session.
            reason: Revocation reason string (default ``"guardian_request"``).
            request: Optional FastAPI request for IP extraction.

        Returns:
            int: Number of consent records revoked.

        Raises:
            AuthorisationError: When the guardian is not the parent of
                the specified learner.

        Example:
            ::

                count = await svc.revoke_consent(
                    learner_id, guardian_id, db, reason="erasure_request",
                )
                assert count >= 1
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
        """Assert that active parental consent exists for a learner.

        Used as a FastAPI dependency via ``Depends`` to enforce the
        consent gate on every route that accesses learner data.

        Args:
            learner_id: UUID of the learner to check.
            db: Async database session.

        Returns:
            ParentalConsent: The active :class:`~app.models.ParentalConsent`
            record.

        Raises:
            ConsentRequiredError: When no active consent record exists
                for the learner.

        Example:
            ::

                consent = await svc.require_active_consent(learner_id, db)
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
        """Return consent records expiring within a given window.

        Used by the ARQ consent-renewal reminder background job
        (:func:`~app.modules.jobs.send_consent_renewal_reminders`).

        Args:
            db: Async database session.
            days: Number of days until expiry to include (default ``30``).

        Returns:
            list[ParentalConsent]: Consent records expiring within the
            specified window.
        """
        return await _consent_repo.get_expiring_soon(db, days=days)


def _get_ip(request: Request | None) -> str | None:
    """Extract the client IP address from the request headers.

    Args:
        request: FastAPI request object or ``None``.

    Returns:
        The client IP address if available, otherwise ``None``.
    """
    if request is None:
        return None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _get_ua(request: Request | None) -> str | None:
    """Extract the user agent string from the request headers.

    Args:
        request: FastAPI request object or ``None``.

    Returns:
        The User-Agent header value, or ``None`` if unavailable.
    """
    return request.headers.get("User-Agent") if request else None
