"""
EduBoost V2 — Fourth Estate Service (Pillar 4)
Durable, append-only audit trail written directly to PostgreSQL.
Replaces the legacy RabbitMQ/Redis Streams dependency.
"""
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.repositories import AuditRepository

log = get_logger(__name__)


class AuditAction(str, Enum):
    # Auth
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_LOGIN_FAILED = "user.login_failed"
    PASSWORD_CHANGED = "user.password_changed"

    # Consent (POPIA critical)
    CONSENT_GRANTED = "consent.granted"
    CONSENT_REVOKED = "consent.revoked"
    CONSENT_EXPIRED = "consent.expired"
    CONSENT_RENEWED = "consent.renewed"

    # Learner data
    LEARNER_CREATED = "learner.created"
    LEARNER_UPDATED = "learner.updated"
    LEARNER_ERASED = "learner.erased"
    LEARNER_DATA_EXPORTED = "learner.data_exported"

    # Diagnostics
    DIAGNOSTIC_SESSION_STARTED = "diagnostic.session_started"
    DIAGNOSTIC_SESSION_COMPLETED = "diagnostic.session_completed"

    # Lessons
    LESSON_GENERATED = "lesson.generated"
    LESSON_VIEWED = "lesson.viewed"

    # Study plans
    STUDY_PLAN_CREATED = "study_plan.created"
    STUDY_PLAN_UPDATED = "study_plan.updated"

    # RLHF
    FEEDBACK_SUBMITTED = "feedback.submitted"

    # Admin
    ADMIN_ACTION = "admin.action"


def _sanitise_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Strip known PII keys from audit metadata."""
    pii_keys = {"email", "password", "phone", "id_number", "address", "name"}
    return {
        k: "[REDACTED]" if k.lower() in pii_keys else v
        for k, v in data.items()
    }


async def write_audit_event(
    db: AsyncSession,
    *,
    action: AuditAction | str,
    actor_id: UUID | str | None = None,
    learner_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    svc = FourthEstateService(db)
    safe_metadata = _sanitise_metadata(metadata or {})
    payload = {
        **safe_metadata,
        "resource_type": resource_type,
        "ip_address": ip_address,
        "user_agent": user_agent,
    }
    if learner_id:
        payload["learner_id"] = str(learner_id)
    await svc.record(
        event_type=str(action),
        actor_id=str(actor_id) if actor_id else None,
        resource_id=resource_id,
        payload=payload,
    )


async def write_audit_event_background(
    db: AsyncSession,
    **kwargs: Any,
) -> None:
    try:
        await write_audit_event(db, **kwargs)
        await db.commit()
    except Exception as exc:
        log.error("Background audit write failed: %s", exc)


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
        resource_id: str | None = None,
        payload: dict | None = None,
        constitutional_outcome: str | None = None,
    ) -> None:
        entry = await self._repo.log(
            event_type=event_type,
            actor_id=actor_id,
            learner_pseudonym=learner_pseudonym,
            payload={
                **(payload or {}),
            },
            constitutional_outcome=constitutional_outcome,
        )
        try:
            log.info(
                "audit_event",
                event_type=event_type,
                actor=actor_id,
                pseudonym=learner_pseudonym,
                outcome=constitutional_outcome,
                audit_id=str(entry.id),
            )
        except AttributeError:
            # Some test logging setups expose a minimal logger without the
            # stdlib attributes structlog processors expect. The audit record
            # itself is the source of truth, so logging must not break the
            # protected action.
            pass

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
        await self.record(event.lower(), actor_id=actor_id, payload=detail or {})

    async def access_rejected(self, actor_id: str | None, learner_id: str, reason: str) -> None:
        await self.record(
            "consent.access_rejected",
            actor_id=actor_id,
            payload={"learner_id": learner_id, "reason": reason},
            constitutional_outcome="REJECTED",
        )

    async def subscription_changed(self, guardian_id: str, new_tier: str, stripe_event_id: str) -> None:
        await self.record(
            "SUBSCRIPTION_CHANGED",
            actor_id=guardian_id,
            payload={"new_tier": new_tier, "stripe_event_id": stripe_event_id},
            constitutional_outcome="APPROVED",
        )
