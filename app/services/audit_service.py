"""
EduBoost V2 — Audit Service
Durable, append-only audit trail for compliance and security monitoring.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.audit_repository import AuditRepository

log = get_logger(__name__)


class AuditService:
    """
    Consolidated Audit Service.
    Records every sensitive action as an immutable audit event in the database.
    """

    def __init__(self, db: AsyncSession | None = None, repository: AuditRepository | None = None) -> None:
        if repository:
            self._repo = repository
        elif db:
            self._repo = AuditRepository(db)
        else:
            self._repo = None

    async def record(
        self,
        event_type: str,
        actor_id: str | UUID | None = None,
        learner_pseudonym: str | UUID | None = None,
        resource_id: str | UUID | None = None,
        payload: dict[str, Any] | None = None,
        constitutional_outcome: str | None = None,
        db: AsyncSession | None = None,
    ) -> Any:
        """Low-level record method."""
        repo = self._repo
        if db:
            repo = AuditRepository(db)
        
        if not repo:
            log.warning("audit_service_no_repository", event_type=event_type)
            return None

        entry = await repo.append(
            event_type=event_type,
            payload={
                **(payload or {}),
                **({"learner_pseudonym": str(learner_pseudonym)} if learner_pseudonym else {}),
                **({"constitutional_outcome": constitutional_outcome} if constitutional_outcome else {}),
            },
            actor_id=actor_id,
            resource_id=resource_id,
        )
        log.info(
            "audit_event",
            event_type=event_type,
            actor=str(actor_id) if actor_id else None,
            pseudonym=str(learner_pseudonym) if learner_pseudonym else None,
            outcome=constitutional_outcome,
            audit_id=str(getattr(entry, "id", getattr(entry, "event_id", ""))),
        )
        return entry

    # ── Convenience helpers ───────────────────────────────────────────────────

    async def consent_granted(self, guardian_id: str | UUID, learner_id: str | UUID, policy_version: str) -> None:
        await self.record(
            "CONSENT_GRANTED",
            actor_id=guardian_id,
            resource_id=learner_id,
            payload={"policy_version": policy_version},
            constitutional_outcome="APPROVED",
        )

    async def consent_revoked(self, guardian_id: str | UUID, learner_id: str | UUID) -> None:
        await self.record(
            "CONSENT_REVOKED",
            actor_id=guardian_id,
            resource_id=learner_id,
            constitutional_outcome="APPROVED",
        )

    async def erasure_requested(self, guardian_id: str | UUID, learner_pseudonym: str | UUID) -> None:
        await self.record(
            "ERASURE_REQUESTED",
            actor_id=guardian_id,
            learner_pseudonym=learner_pseudonym,
            constitutional_outcome="APPROVED",
        )

    async def erasure_executed(self, learner_pseudonym: str | UUID) -> None:
        await self.record(
            "ERASURE_EXECUTED",
            learner_pseudonym=learner_pseudonym,
            constitutional_outcome="APPROVED",
        )

    async def lesson_generated(self, learner_pseudonym: str | UUID, subject: str, topic: str, provider: str) -> None:
        await self.record(
            "LESSON_GENERATED",
            learner_pseudonym=learner_pseudonym,
            payload={"subject": subject, "topic": topic, "provider": provider},
            constitutional_outcome="APPROVED",
        )

    async def constitutional_violation(self, learner_pseudonym: str | UUID, reason: str) -> None:
        await self.record(
            "CONSTITUTIONAL_VIOLATION",
            learner_pseudonym=learner_pseudonym,
            payload={"reason": reason},
            constitutional_outcome="REJECTED",
        )

    async def auth_event(self, event: str, actor_id: str | UUID, detail: dict[str, Any] | None = None) -> None:
        await self.record(event.lower(), actor_id=actor_id, payload=detail or {})

    async def access_rejected(self, actor_id: str | UUID | None, learner_id: str | UUID, reason: str) -> None:
        await self.record(
            "consent.access_rejected",
            actor_id=actor_id,
            resource_id=learner_id,
            payload={"reason": reason},
            constitutional_outcome="REJECTED",
        )

    async def subscription_changed(self, guardian_id: str | UUID, new_tier: str, stripe_event_id: str) -> None:
        await self.record(
            "SUBSCRIPTION_CHANGED",
            actor_id=guardian_id,
            payload={"new_tier": new_tier, "stripe_event_id": stripe_event_id},
            constitutional_outcome="APPROVED",
        )

    # ── Legacy V2 Helpers ─────────────────────────────────────────────────────

    async def log_event(self, event_type: str, payload: dict | None = None, learner_id: str | None = None, actor_id: str | None = None) -> Any:
        entry = await self.record(
            event_type=event_type,
            payload=payload,
            resource_id=learner_id,
            actor_id=actor_id,
        )
        from app.domain.schemas import AuditLogEntry
        return AuditLogEntry(
            event_id=str(getattr(entry, "id", getattr(entry, "event_id", ""))),
            learner_id=getattr(entry, "learner_id", getattr(entry, "learner_pseudonym", None)),
            event_type=getattr(entry, "event_type", ""),
            occurred_at=getattr(entry, "occurred_at", getattr(entry, "created_at", datetime.now(UTC))),
            payload=getattr(entry, "payload", {}) or {},
        )

    async def get_recent_events(self, limit: int = 50) -> list[Any]:
        if self._repo and hasattr(self._repo, "latest"):
            return await self._repo.latest(limit=limit)
        return []

