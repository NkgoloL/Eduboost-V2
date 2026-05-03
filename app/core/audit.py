"""
EduBoost V2 — Fourth Estate Service (Pillar 4)
Durable, append-only audit trail written directly to PostgreSQL.
Replaces the legacy RabbitMQ/Redis Streams dependency.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.repositories import AuditRepository

log = get_logger(__name__)


class FourthEstateService:
    """
    Constitutional Pillar 4: The Fourth Estate.
    Records every sensitive action as an immutable audit event.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._repo = AuditRepository(db)

    async def record(
        self,
        event_type: str,
        actor_id: str | None = None,
        learner_pseudonym: str | None = None,
        payload: dict | None = None,
        constitutional_outcome: str | None = None,
    ) -> None:
        entry = await self._repo.log(
            event_type=event_type,
            actor_id=actor_id,
            learner_pseudonym=learner_pseudonym,
            payload=payload,
            constitutional_outcome=constitutional_outcome,
        )
        log.info(
            "audit_event",
            event_type=event_type,
            actor=actor_id,
            pseudonym=learner_pseudonym,
            outcome=constitutional_outcome,
            audit_id=entry.id,
        )

    # ── Convenience helpers ───────────────────────────────────────────────────

    async def consent_granted(self, guardian_id: str, learner_id: str, policy_version: str) -> None:
        await self.record(
            "CONSENT_GRANTED",
            actor_id=guardian_id,
            payload={"learner_id": learner_id, "policy_version": policy_version},
            constitutional_outcome="APPROVED",
        )

    async def consent_revoked(self, guardian_id: str, learner_id: str) -> None:
        await self.record(
            "CONSENT_REVOKED",
            actor_id=guardian_id,
            payload={"learner_id": learner_id},
            constitutional_outcome="APPROVED",
        )

    async def erasure_requested(self, guardian_id: str, learner_pseudonym: str) -> None:
        await self.record(
            "ERASURE_REQUESTED",
            actor_id=guardian_id,
            learner_pseudonym=learner_pseudonym,
            payload={"event": "erasure_requested"},
            constitutional_outcome="APPROVED",
        )

    async def erasure_executed(self, learner_pseudonym: str) -> None:
        await self.record(
            "ERASURE_EXECUTED",
            learner_pseudonym=learner_pseudonym,
            payload={"event": "erasure_executed"},
            constitutional_outcome="APPROVED",
        )

    async def lesson_generated(self, learner_pseudonym: str, subject: str, topic: str, provider: str) -> None:
        await self.record(
            "LESSON_GENERATED",
            learner_pseudonym=learner_pseudonym,
            payload={"subject": subject, "topic": topic, "provider": provider},
            constitutional_outcome="APPROVED",
        )

    async def constitutional_violation(self, learner_pseudonym: str, reason: str) -> None:
        await self.record(
            "CONSTITUTIONAL_VIOLATION",
            learner_pseudonym=learner_pseudonym,
            payload={"reason": reason},
            constitutional_outcome="REJECTED",
        )

    async def auth_event(self, event: str, actor_id: str, detail: dict | None = None) -> None:
        await self.record(event, actor_id=actor_id, payload=detail or {})

    async def subscription_changed(self, guardian_id: str, new_tier: str, stripe_event_id: str) -> None:
        await self.record(
            "SUBSCRIPTION_CHANGED",
            actor_id=guardian_id,
            payload={"new_tier": new_tier, "stripe_event_id": stripe_event_id},
            constitutional_outcome="APPROVED",
        )
