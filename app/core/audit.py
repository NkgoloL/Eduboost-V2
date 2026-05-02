"""
EduBoost SA — POPIA Audit Trail
Async audit log writer backed by PostgreSQL.
Replaces the V1 RabbitMQ / fourth_estate.py approach.

Design:
- Writes in the SAME transaction as the audited operation → transactionally consistent.
- For non-critical audit events, uses FastAPI BackgroundTasks for non-blocking writes.
- All events are queryable and exportable for POPIA right-of-access requests.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AuditAction(StrEnum):
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
    LEARNER_ERASED = "learner.erased"              # POPIA right to erasure
    LEARNER_DATA_EXPORTED = "learner.data_exported"  # POPIA right of access

    # Diagnostics
    DIAGNOSTIC_SESSION_STARTED = "diagnostic.session_started"
    DIAGNOSTIC_SESSION_COMPLETED = "diagnostic.session_completed"

    # Lessons (LLM calls — pseudonymised)
    LESSON_GENERATED = "lesson.generated"
    LESSON_VIEWED = "lesson.viewed"

    # Study plans
    STUDY_PLAN_CREATED = "study_plan.created"
    STUDY_PLAN_UPDATED = "study_plan.updated"

    # RLHF
    FEEDBACK_SUBMITTED = "feedback.submitted"

    # Admin
    ADMIN_ACTION = "admin.action"


async def write_audit_event(
    db: AsyncSession,
    *,
    action: AuditAction | str,
    actor_id: UUID | str | None,
    learner_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """
    Write a POPIA audit event within the current DB session.
    Committed atomically with the parent operation.

    Usage:
        async with db.begin():
            await consent_repo.revoke(learner_id, db)
            await write_audit_event(
                db,
                action=AuditAction.CONSENT_REVOKED,
                actor_id=guardian_id,
                learner_id=learner_id,
            )
            # Both committed together — no partial state possible.
    """
    from app.models.audit_log import AuditLog  # avoid circular import

    # Sanitise metadata — never log raw PII
    safe_metadata = _sanitise_metadata(metadata or {})

    entry = AuditLog(
        action=str(action),
        actor_id=str(actor_id) if actor_id else None,
        learner_id=learner_id,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=json.dumps(safe_metadata),
        ip_address=ip_address,
        user_agent=user_agent,
        occurred_at=datetime.now(UTC),
    )
    db.add(entry)
    # Will be committed with the parent transaction.


async def write_audit_event_background(
    db: AsyncSession,
    **kwargs: Any,
) -> None:
    """
    Non-blocking audit write for low-criticality events.
    Use FastAPI's BackgroundTasks to call this after response is sent.
    For POPIA-critical events (consent changes, data erasure), use write_audit_event()
    with transactional consistency instead.
    """
    try:
        await write_audit_event(db, **kwargs)
        await db.commit()
    except Exception as exc:
        logger.error("Background audit write failed: %s", exc, exc_info=True)


def _sanitise_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Strip known PII keys from audit metadata."""
    PII_KEYS = {"email", "password", "phone", "id_number", "address", "name"}
    return {
        k: "[REDACTED]" if k.lower() in PII_KEYS else v
        for k, v in data.items()
    }
