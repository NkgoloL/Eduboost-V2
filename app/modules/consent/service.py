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
from app.core.consent_policy import ConsentPolicyDecision, derive_consent_state
from app.core.exceptions import ConsentExpiredError, ConsentRequiredError
from app.models import ParentalConsent
from app.repositories.audit_repository import AuditRepository
from app.repositories.repositories import ConsentRepository
from app.utils.versioning import (
    VersionChangeType,
    detect_version_change,
    requires_manual_renewal,
)


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

    # Current required policy version - should be configurable via env/config
    REQUIRED_POLICY_VERSION = "1.0.0"

    def __init__(
        self,
        db: AsyncSession | None = None,
        *,
        consent_repo: ConsentRepository | None = None,
        audit_repo: AuditRepository | None = None,
        required_policy_version: str | None = None,
    ) -> None:
        """Initialise the consent service with repository dependencies.

        Args:
            db: Optional async database session.  Required when explicit
                repositories are not provided.
            consent_repo: Optional :class:`~app.repositories.consent_repository.ConsentRepository`
                instance.  Created from ``db`` if not supplied.
            audit_repo: Optional :class:`~app.repositories.audit_repository.AuditRepository`
                instance.  Created from ``db`` if not supplied.
            required_policy_version: Optional required policy version string.
                Defaults to class constant if not provided.

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
        self._required_policy_version = required_policy_version or self.REQUIRED_POLICY_VERSION

    async def consent_decision(self, learner_id: str) -> ConsentPolicyDecision:
        """Return the canonical consent-state decision for a learner."""
        consent = await self._repo.get_latest_for_learner(str(learner_id))
        decision = derive_consent_state(consent, learner_id=str(learner_id))

        # Check if consent is stale due to policy version change
        if consent and decision.active:
            if self._is_consent_stale(consent.policy_version):
                from app.models import ConsentState
                from app.core.consent_policy import ConsentPolicyDecision
                # Create new decision with stale consent status
                decision = ConsentPolicyDecision(
                    learner_id=decision.learner_id,
                    state=ConsentState.RENEWAL_REQUIRED,
                    active=False,
                    reason=f"Consent version {consent.policy_version} is stale; required version is {self._required_policy_version}",
                    policy_version=consent.policy_version,
                    privacy_notice_version=decision.privacy_notice_version,
                    granted_at=decision.granted_at,
                    expires_at=decision.expires_at,
                    revoked_at=decision.revoked_at,
                    renewal_due_at=decision.renewal_due_at,
                )

        return decision

    def _is_consent_stale(self, consent_version: str) -> bool:
        """Check if consent version is stale compared to required version."""
        try:
            return requires_manual_renewal(consent_version, self._required_policy_version)
        except ValueError:
            # If version parsing fails, treat as stale to be safe
            return True

    def detect_version_change_type(self, current_version: str, new_version: str) -> VersionChangeType:
        """Detect the type of version change between two consent versions."""
        try:
            return detect_version_change(current_version, new_version)
        except ValueError:
            # If version parsing fails, assume major change (safest)
            return VersionChangeType.MAJOR

    async def require_active_consent(self, learner_id: str, actor_id: str | None = None) -> ConsentPolicyDecision:
        """Enforce active consent for a learner.

        Returns the policy decision when processing may proceed. Pending,
        expired, denied, or withdrawn states are audited and blocked.
        """
        decision = await self.consent_decision(str(learner_id))
        if not decision.active:
            await self._append_audit(
                "consent.access_rejected",
                actor_id=actor_id,
                resource_id=learner_id,
                payload={"learner_id": str(learner_id), "reason": decision.reason, "state": decision.state.value},
            )
            if decision.state.value == "expired":
                raise ConsentExpiredError("Guardian consent has expired")
            raise ConsentRequiredError("Active parental consent required")
        return decision

    async def grant(
        self,
        guardian_id: str,
        learner_id: str,
        consent_version: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        ip_hash: str | None = None,
    ) -> ParentalConsent:
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
            state="granted",
        )
        await self._append_audit(
            "consent.granted",
            actor_id=guardian_id,
            resource_id=consent.id,
            payload={"learner_id": str(learner_id), "consent_version": consent_version, "state": "granted"},
        )
        # Record version history entry
        await self._record_version_history(consent, "granted", "initial_grant")
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
                payload={"learner_id": str(learner_id), "reason": reason, "state": "withdrawn"},
            )
            # Record version history entry
            await self._record_version_history(active, "withdrawn", reason)
        return count

    async def renew(self, guardian_id: str, learner_id: str, consent_version: str) -> ParentalConsent:
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
        # Get current consent to detect version change type
        current = await self._repo.get_latest_for_learner(str(learner_id))
        current_version = current.policy_version if current else "0.0.0"

        change_type = self.detect_version_change_type(current_version, consent_version)

        # For PATCH changes (same MAJOR.MINOR), auto-renewal is allowed
        # For MAJOR/MINOR changes, manual renewal is required (already handled by caller)
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
                "change_type": change_type.value,
            },
        )
        # Record version history entry for renewed consent
        await self._record_version_history(renewed, "granted", f"renewed_from_{getattr(previous, 'policy_version', 'unknown')}")
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

    async def get_status(self, learner_id: str) -> ParentalConsent | None:
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
        return await self._repo.get_latest_for_learner(str(learner_id))

    async def get_expiring_consents(self, db: AsyncSession | None = None, days: int = 30) -> list[ParentalConsent]:
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

    async def _record_version_history(self, consent: ParentalConsent, status: str, transition_reason: str) -> None:
        """Record a consent version history entry for audit trail.

        Args:
            consent: The consent record to snapshot.
            status: The consent status at this point in time.
            transition_reason: Reason for the state transition.
        """
        from app.models import ConsentVersionHistory

        if self._db is None:
            return

        history_entry = ConsentVersionHistory(
            consent_id=consent.id,
            policy_version=consent.policy_version,
            status=status,
            granted_at=consent.granted_at,
            expires_at=consent.expires_at,
            revoked_at=consent.revoked_at,
            transition_reason=transition_reason,
        )
        self._db.add(history_entry)
        await self._db.flush()
