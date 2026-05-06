"""POPIA parental consent lifecycle service.

Enforces active parental consent before learner data or lesson generation
can proceed.  All operations are audited for South African POPIA
compliance using either a provided
:class:`~app.repositories.audit_repository.AuditRepository` or the
:class:`~app.core.audit.FourthEstateService` fallback.

Every consent state change (grant, revoke, renew, erasure) is recorded
in the audit trail for compliance and investigation.

Example:
    Check and enforce consent before accessing learner data::

        from app.modules.consent.service import ConsentService

        svc = ConsentService(db)
        await svc.require_active_consent("learner-uuid", actor_id="user-uuid")
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import FourthEstateService
from app.core.exceptions import ConsentRequiredError
from app.repositories.audit_repository import AuditRepository
from app.repositories.consent_repository import ConsentRepository


class ConsentService:
    """Async POPIA consent lifecycle service.

    Exposes operations to grant, revoke, renew, and query parental
    consent records.  Every consent state change is recorded in the
    audit trail via :class:`~app.repositories.audit_repository.AuditRepository`
    or :class:`~app.core.audit.FourthEstateService`.

    Example:
        ::

            svc = ConsentService(db)
            consent = await svc.grant(
                guardian_id="g-001", learner_id="l-001",
                consent_version="1.2",
            )
            assert consent is not None
    """

    def __init__(
        self,
        db: AsyncSession | None = None,
        *,
        consent_repo: ConsentRepository | None = None,
        audit_repo: AuditRepository | None = None,
    ) -> None:
        """Initialise the consent service with repository dependencies.

        Args:
            db: Optional async database session.  Required when explicit
                repositories are not provided.
            consent_repo: Optional :class:`~app.repositories.consent_repository.ConsentRepository`
                instance.  Created from ``db`` if not supplied.
            audit_repo: Optional :class:`~app.repositories.audit_repository.AuditRepository`
                instance.  Created from ``db`` if not supplied.

        Raises:
            ValueError: If neither a database session nor a consent
                repository is provided.

        Example:
            ::

                svc = ConsentService(db)  # auto-creates repos
                svc = ConsentService(consent_repo=repo)  # explicit repo
        """
        if consent_repo is None:
            if db is None:
                raise ValueError("ConsentService requires a db session or consent_repo")
            consent_repo = ConsentRepository(db)
        if audit_repo is None and db is not None:
            audit_repo = AuditRepository(db)

        self._db = db
        self._repo = consent_repo
        self._audit_repo = audit_repo

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> None:
        """Enforce active consent for a learner.

        If no active consent exists, an audit event is appended and a
        :class:`~app.core.exceptions.ConsentRequiredError` is raised.

        Args:
            learner_id: Learner identifier to validate consent for.
            actor_id: Optional actor identifier for the audit event.

        Raises:
            ConsentRequiredError: When the learner does not have active
                consent.

        Example:
            ::

                await svc.require_active_consent("l-001", actor_id="u-001")
        """
        consent = await self._repo.get_active(str(learner_id))
        if consent is None:
            await self._append_audit(
                "consent.access_rejected",
                actor_id=actor_id,
                resource_id=learner_id,
                payload={"learner_id": str(learner_id), "reason": "missing_or_expired"},
            )
            raise ConsentRequiredError("Active parental consent required")

    async def grant(
        self,
        guardian_id: str,
        learner_id: str,
        consent_version: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        ip_hash: str | None = None,
    ):
        """Grant a new parental consent record.

        Creates a consent record via
        :meth:`~app.repositories.consent_repository.ConsentRepository.grant`
        and records a ``consent.granted`` audit event.

        Args:
            guardian_id: Guardian identifier granting consent.
            learner_id: Learner identifier covered by the consent.
            consent_version: Version of the consent policy agreed to.
            ip_address: Optional IP address from the guardian's session.
            user_agent: Optional browser user agent string.
            ip_hash: Optional hashed IP for privacy-preserving audit.

        Returns:
            The newly created consent record.

        Example:
            ::

                consent = await svc.grant(
                    "g-001", "l-001", "1.2", ip_address="127.0.0.1",
                )
        """
        # AuditLog / fourth_estate coverage is written via _append_audit below.
        consent = await self._repo.grant(
            learner_id=str(learner_id),
            guardian_id=str(guardian_id),
            consent_version=consent_version,
            ip_address=ip_address or ip_hash,
            user_agent=user_agent,
        )
        await self._append_audit(
            "consent.granted",
            actor_id=guardian_id,
            resource_id=consent.id,
            payload={"learner_id": str(learner_id), "consent_version": consent_version},
        )
        return consent

    async def revoke(self, learner_id: str, guardian_id: str | None = None, reason: str = "revoked") -> int:
        """Revoke existing active consent for a learner.

        Sets consent status to revoked and records a ``consent.revoked``
        audit event.

        Args:
            learner_id: Learner identifier whose consent is revoked.
            guardian_id: Optional guardian identifier for the audit event.
            reason: Revocation reason (e.g. ``"revoked"``,
                ``"erasure_requested"``).

        Returns:
            int: Number of consent records revoked.

        Example:
            ::

                count = await svc.revoke("l-001", guardian_id="g-001")
                assert count >= 1
        """
        # AuditLog / fourth_estate coverage is written via _append_audit below.
        active = await self._repo.get_active(str(learner_id))
        count = await self._repo.revoke(str(learner_id), reason=reason)
        if active is not None:
            await self._append_audit(
                "consent.revoked",
                actor_id=guardian_id,
                resource_id=active.id,
                payload={"learner_id": str(learner_id), "reason": reason},
            )
        return count

    async def renew(self, guardian_id: str, learner_id: str, consent_version: str):
        """Renew an existing consent record with a new policy version.

        Revokes the previous consent and creates a fresh record with
        the updated ``consent_version``.  Records a ``consent.renewed``
        audit event.

        Args:
            guardian_id: Guardian identifier renewing consent.
            learner_id: Learner identifier under consent.
            consent_version: New consent policy version string.

        Returns:
            The renewed consent record.

        Example:
            ::

                renewed = await svc.renew("g-001", "l-001", "2.0")
        """
        previous, renewed = await self._repo.renew(
            learner_id=str(learner_id),
            guardian_id=str(guardian_id),
            consent_version=consent_version,
        )
        await self._append_audit(
            "consent.renewed",
            actor_id=guardian_id,
            resource_id=renewed.id,
            payload={
                "learner_id": str(learner_id),
                "previous_version": getattr(previous, "policy_version", None),
                "new_version": consent_version,
            },
        )
        return renewed

    async def execute_erasure(self, guardian_id: str, learner_id: str) -> None:
        """Execute a POPIA right-to-erasure workflow for a learner.

        Revokes active consent via :meth:`revoke` and records a
        dedicated ``consent.erasure_requested`` audit event for
        compliance purposes.

        Args:
            guardian_id: Guardian identifier requesting erasure.
            learner_id: Learner identifier whose data erasure is
                requested.

        Example:
            ::

                await svc.execute_erasure("g-001", "l-001")
        """
        # AuditLog / fourth_estate coverage is written via _append_audit below.
        await self.revoke(str(learner_id), guardian_id=guardian_id, reason="erasure_requested")
        await self._append_audit(
            "consent.erasure_requested",
            actor_id=guardian_id,
            resource_id=learner_id,
            payload={"learner_id": str(learner_id)},
        )

    async def get_status(self, learner_id: str):
        """Return the current active consent status for a learner.

        Args:
            learner_id: Learner identifier to query.

        Returns:
            Optional consent record, or ``None`` if no active consent
            exists.

        Example:
            ::

                consent = await svc.get_status("l-001")
                if consent is None:
                    print("No active consent")
        """
        return await self._repo.get_active(str(learner_id))

    async def get_expiring_consents(self, db: AsyncSession | None = None, days: int = 30):
        """Return consent records expiring within a given window.

        Used by the ARQ consent-renewal reminder background job
        (:func:`~app.modules.jobs.send_consent_renewal_reminders`).

        Args:
            db: Optional database session.  Falls back to the service's
                configured session via the repository.
            days: Number of days until expiry to include (default ``30``).

        Returns:
            A list of consent records expiring within the window.
        """
        return await self._repo.get_expiring_soon(db, days=days)

    async def _append_audit(
        self,
        event_type: str,
        *,
        actor_id: str | None,
        resource_id: str | None,
        payload: dict,
    ) -> None:
        """Persist an audit event for a consent lifecycle operation.

        Tries :class:`~app.repositories.audit_repository.AuditRepository`
        first; falls back to :class:`~app.core.audit.FourthEstateService`
        if no audit repository was configured.

        Args:
            event_type: Event type string (e.g. ``"consent.granted"``,
                ``"consent.revoked"``).
            actor_id: Optional actor identifier to attribute the event.
            resource_id: Optional resource identifier for the event.
            payload: Event payload metadata dictionary.
        """
        if self._audit_repo is not None:
            await self._audit_repo.append(
                event_type=event_type,
                actor_id=actor_id,
                resource_id=resource_id,
                payload=payload,
            )
            return
        if self._db is not None:
            await FourthEstateService(self._db).record(
                event_type=event_type,
                actor_id=actor_id,
                payload=payload,
            )
