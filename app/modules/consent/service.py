"""POPIA consent service for EduBoost V2.

This service enforces active parental consent before learner data or
lesson generation can proceed. All operations are audited for South African
POPIA compliance using either a provided audit repository or the
FourthEstate audit service fallback.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import FourthEstateService
from app.core.exceptions import ConsentRequiredError
from app.repositories.audit_repository import AuditRepository
from app.repositories.consent_repository import ConsentRepository


class ConsentService:
    """Async POPIA consent lifecycle service.

    The service exposes operations to grant, revoke, renew, and query
    parental consent records. Every consent state change is recorded in the
    audit trail for compliance and investigation.
    """

    def __init__(
        self,
        db: AsyncSession | None = None,
        *,
        consent_repo: ConsentRepository | None = None,
        audit_repo: AuditRepository | None = None,
    ) -> None:
        """Initialize the consent service.

        Args:
            db: Optional async database session. Required when explicit
                repositories are not provided.
            consent_repo: Optional consent repository instance.
            audit_repo: Optional audit repository instance.

        Raises:
            ValueError: If neither a database session nor a consent repository
                is provided.
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
        """Require an active consent record for a learner.

        If no active consent exists for the learner, an audit event is
        appended and a :class:`app.core.exceptions.ConsentRequiredError` is raised.

        Args:
            learner_id: Learner identifier to validate consent for.
            actor_id: Optional actor identifier to attribute the audit event.

        Raises:
            ConsentRequiredError: When the learner does not have active consent.
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

        Args:
            guardian_id: Guardian identifier granting consent.
            learner_id: Learner identifier covered by the consent.
            consent_version: Version of the consent policy agreed to.
            ip_address: Optional IP address from the guardian's session.
            user_agent: Optional browser user agent string.
            ip_hash: Optional hashed IP address for privacy-preserving audit.

        Returns:
            The newly created consent record.
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

        Args:
            learner_id: Learner identifier whose consent should be revoked.
            guardian_id: Optional guardian identifier for the audit event.
            reason: Reason for revocation, such as ``"revoked"`` or
                ``"erasure_requested"``.

        Returns:
            int: Number of consent records revoked.
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

        Args:
            guardian_id: Guardian identifier renewing consent.
            learner_id: Learner identifier under consent.
            consent_version: New consent policy version string.

        Returns:
            The renewed consent record.
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
        """Execute a right-to-erasure workflow for a learner.

        This revokes active consent and records a dedicated erasure request
        audit event for compliance purposes.

        Args:
            guardian_id: Guardian identifier requesting erasure.
            learner_id: Learner identifier whose data erasure is requested.
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
            Optional active consent record, or ``None`` if no active consent exists.
        """
        return await self._repo.get_active(str(learner_id))

    async def get_expiring_consents(self, db: AsyncSession | None = None, days: int = 30):
        """Return consent records that will expire within a given window.

        Args:
            db: Optional database session. If not provided, the service's
                configured session is used by the repository.
            days: Number of days until expiry to include.

        Returns:
            A list of consent records expiring soon.
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
        """Persist an audit event for consent lifecycle operations.

        Args:
            event_type: Event type string, such as ``"consent.granted"``.
            actor_id: Optional actor identifier to attribute the event.
            resource_id: Optional resource identifier for the event.
            payload: Event payload metadata.
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
