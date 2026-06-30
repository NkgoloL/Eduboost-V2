# DEPRECATED: This asyncpg-style consent service is no longer wired to FastAPI v2 routers.
# Canonical consent service: app.modules.consent.service.ConsentService
# This file will be removed after all call sites are migrated. See roadmap P0-01.
# Do not emit an import-time DeprecationWarning here; tests may run with warnings as errors.

"""
app/services/consent_service.py
Orchestrates all §4.1 consent lifecycle flows.
Every state transition is audited (§4.5).
"""
from __future__ import annotations
from app.services.runtime_audit_facade import record_runtime_audit_event
from app.services.runtime_consent_facade import emit_consent_runtime_event

import uuid
from typing import Optional

from app.domain.consent import (
    AuditEventType,
    ConsentRecord,
    ConsentState,
    RENEWAL_WARNING_DAYS,
)
from app.repositories.audit_repository import AuditRepository
from app.repositories.consent_repository import ConsentRepository


class ConsentService:
    def __init__(
        self,
        consent_repo: ConsentRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self._consent = consent_repo
        self._audit = audit_repo

    # ------------------------------------------------------------------
    # §4.1 Grant
    # ------------------------------------------------------------------

    async def grant(
        self,
        learner_id: uuid.UUID,
        guardian_id: uuid.UUID,
        privacy_notice_version: str,
        actor_id: uuid.UUID,
    ) -> ConsentRecord:
        # audit_log
        # runtime-audit-facade-wired
        audit_repository = locals().get('audit_repository') or locals().get('audit_repo') or (getattr(self, 'audit_repository', None) if 'self' in locals() else None)
        if audit_repository is not None:
            await record_runtime_audit_event(audit_repository, action='consent.granted', candidate_name='consent_audit_events', actor_id=str(locals().get('actor_id') or locals().get('user_id') or ''), learner_id=str(locals().get('learner_id') or locals().get('child_id') or ''), resource_type='learner_consent', metadata={'wired_function': 'grant'})
        existing = await self._consent.get_active_for_learner(learner_id)
        if existing:
            updated = existing.grant(privacy_notice_version)
            record = await self._consent.update(updated)
        else:
            new_record = ConsentRecord(
                learner_id=learner_id,
                guardian_id=guardian_id,
                privacy_notice_version=privacy_notice_version,
                state=ConsentState.PENDING,
            ).grant(privacy_notice_version)
            record = await self._consent.create(new_record)

        await self._audit.record(
            AuditEventType.CONSENT_GRANT,
            actor_id=actor_id,
            learner_id=learner_id,
            payload={
                "consent_id": str(record.id),
                "privacy_notice_version": privacy_notice_version,
                "expires_at": record.expires_at.isoformat() if record.expires_at else None,
            },
        )
        return record

    # ------------------------------------------------------------------
    # §4.1 Denial
    # ------------------------------------------------------------------

    async def deny(
        self,
        learner_id: uuid.UUID,
        guardian_id: uuid.UUID,
        privacy_notice_version: str,
        actor_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> ConsentRecord:
        existing = await self._consent.get_active_for_learner(learner_id)
        if existing:
            updated = existing.deny(reason)
            record = await self._consent.update(updated)
        else:
            new_record = ConsentRecord(
                learner_id=learner_id,
                guardian_id=guardian_id,
                privacy_notice_version=privacy_notice_version,
            ).deny(reason)
            record = await self._consent.create(new_record)

        await self._audit.record(
            AuditEventType.CONSENT_DENIAL,
            actor_id=actor_id,
            learner_id=learner_id,
            payload={"consent_id": str(record.id), "reason": reason},
        )
        return record

    # ------------------------------------------------------------------
    # §4.1 Withdrawal
    # ------------------------------------------------------------------

    async def withdraw(
        self,
        learner_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> ConsentRecord:
        record = await self._require_consent_record(learner_id)
        updated = record.withdraw()
        saved = await self._consent.update(updated)
        await self._audit.record(
            AuditEventType.CONSENT_WITHDRAWAL,
            actor_id=actor_id,
            learner_id=learner_id,
            payload={"consent_id": str(saved.id)},
        )
        return saved

    # ------------------------------------------------------------------
    # §4.1 Renewal
    # ------------------------------------------------------------------

    async def renew(
        self,
        learner_id: uuid.UUID,
        actor_id: uuid.UUID,
        privacy_notice_version: str,
    ) -> ConsentRecord:
        record = await self._require_consent_record(learner_id)
        updated = record.renew(privacy_notice_version)
        saved = await self._consent.update(updated)
        await self._audit.record(
            AuditEventType.CONSENT_RENEWAL,
            actor_id=actor_id,
            learner_id=learner_id,
            payload={
                "consent_id": str(saved.id),
                "new_expires_at": saved.expires_at.isoformat() if saved.expires_at else None,
            },
        )
        return saved

    # ------------------------------------------------------------------
    # §4.1 Expiry handling (called by scheduled job)
    # ------------------------------------------------------------------

    async def process_expiry(self, learner_id: uuid.UUID) -> ConsentRecord:
        record = await self._require_consent_record(learner_id)
        updated = record.mark_expired()
        saved = await self._consent.update(updated)
        await self._audit.record(
            AuditEventType.CONSENT_EXPIRY,
            actor_id=None,
            learner_id=learner_id,
            payload={"consent_id": str(saved.id)},
        )
        return saved

    # ------------------------------------------------------------------
    # §4.1 Restricted mode check
    # ------------------------------------------------------------------

    async def assert_active_consent(self, learner_id: uuid.UUID) -> ConsentRecord:
        """
        Raises PermissionError if consent is not active.
        Used by §4.2 declarative dependency.
        """
        record = await self._consent.get_active_for_learner(learner_id)
        if record is None or not record.is_active():
            raise PermissionError(
                f"No active POPIA consent for learner {learner_id}. "
                "Access is restricted until consent is granted."
            )
        return record

    # ------------------------------------------------------------------
    # §4.1 P1 – expiry notification schedule
    # ------------------------------------------------------------------

    async def flag_approaching_renewals(self) -> list[ConsentRecord]:
        """
        Called by a scheduler.  Marks GRANTED records approaching expiry
        as RENEWAL_REQUIRED so guardians can be notified.
        """
        candidates = await self._consent.list_expiring_soon(within_days=RENEWAL_WARNING_DAYS)
        flagged: list[ConsentRecord] = []
        for record in candidates:
            if record.days_until_expiry() is not None:
                updated = record.mark_renewal_required()
                saved = await self._consent.update(updated)
                await self._audit.record(
                    AuditEventType.CONSENT_EXPIRY,
                    actor_id=None,
                    learner_id=record.learner_id,
                    payload={
                        "consent_id": str(saved.id),
                        "note": "renewal_required flagged by scheduler",
                    },
                )
                flagged.append(saved)
        return flagged

    # ------------------------------------------------------------------

    async def _require_consent_record(self, learner_id: uuid.UUID) -> ConsentRecord:
        record = await self._consent.get_active_for_learner(learner_id)
        if record is None:
            raise ValueError(f"No consent record found for learner {learner_id}")
        return record

    # runtime-consent-facade-ready
    async def _emit_runtime_consent_audit(self, *, action: str, learner_id: str, actor_id: str | None = None, metadata: dict | None = None):
        repo = getattr(self, 'audit_repository', None) or getattr(self, 'audit_repo', None)
        return await emit_consent_runtime_event(action=action, learner_id=str(learner_id), actor_id=actor_id, audit_repository=repo, metadata=metadata or {})
