"""EduBoost V2 — Consent Service (POPIA Gate)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import FourthEstateService
from app.core.exceptions import ConsentRequiredError
from app.repositories.audit_repository import AuditRepository
from app.repositories.consent_repository import ConsentRepository


class ConsentService:
    def __init__(
        self,
        db: AsyncSession | None = None,
        *,
        consent_repo: ConsentRepository | None = None,
        audit_repo: AuditRepository | None = None,
    ) -> None:
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
        # AuditLog / fourth_estate coverage is written via _append_audit below.
        await self.revoke(str(learner_id), guardian_id=guardian_id, reason="erasure_requested")
        await self._append_audit(
            "consent.erasure_requested",
            actor_id=guardian_id,
            resource_id=learner_id,
            payload={"learner_id": str(learner_id)},
        )

    async def get_status(self, learner_id: str):
        return await self._repo.get_active(str(learner_id))

    async def get_expiring_consents(self, db: AsyncSession | None = None, days: int = 30):
        return await self._repo.get_expiring_soon(db, days=days)

    async def _append_audit(
        self,
        event_type: str,
        *,
        actor_id: str | None,
        resource_id: str | None,
        payload: dict,
    ) -> None:
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
