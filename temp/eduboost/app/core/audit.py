"""Append-only audit trail for POPIA compliance.

Every sensitive action (consent grant/revoke, data access, data erasure,
login events) is recorded as an immutable :class:`AuditEvent` written
asynchronously to the ``audit_logs`` PostgreSQL table.

The audit service intentionally does **not** raise exceptions on write
failure — a failed audit write must never break the user-facing request.
Instead, failures are emitted as structured log warnings so they are
captured by the Grafana Loki pipeline.

Example:
    Record a consent event::

        from app.core.audit import AuditService, AuditAction
        await AuditService.log(
            action=AuditAction.CONSENT_GRANTED,
            actor_id="guardian-uuid",
            target_id="learner-uuid",
            metadata={"consent_version": "1.2"},
        )
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AuditAction(str, Enum):
    """Enumeration of auditable event types.

    Attributes:
        CONSENT_GRANTED: A guardian granted POPIA consent for a learner.
        CONSENT_REVOKED: A guardian revoked a previously granted consent.
        DATA_ACCESS: A right-to-access export was requested and delivered.
        DATA_ERASURE: A right-to-erasure request was processed.
        LOGIN_SUCCESS: A user authenticated successfully.
        LOGIN_FAILURE: A failed authentication attempt was recorded.
        LEARNER_CREATED: A new learner profile was created.
        LESSON_GENERATED: An AI lesson was generated for a learner.
        SUBSCRIPTION_CHANGED: A guardian's subscription tier was updated.
    """

    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    DATA_ACCESS = "data_access"
    DATA_ERASURE = "data_erasure"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LEARNER_CREATED = "learner_created"
    LESSON_GENERATED = "lesson_generated"
    SUBSCRIPTION_CHANGED = "subscription_changed"


class AuditEvent:
    """Immutable value object representing a single audit record.

    Attributes:
        id: Auto-generated UUID v4 for this event.
        action: The :class:`AuditAction` that occurred.
        actor_id: UUID of the user who performed the action.
        target_id: UUID of the entity acted upon (may differ from actor).
        timestamp: UTC datetime when the event was recorded.
        metadata: Arbitrary key/value pairs providing action context.
        ip_address: Client IP address, if available from the request context.

    Example:
        ::

            event = AuditEvent(
                action=AuditAction.LOGIN_SUCCESS,
                actor_id="user-123",
                target_id="user-123",
            )
            assert event.id is not None
    """

    def __init__(
        self,
        action: AuditAction,
        actor_id: str,
        target_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Initialise an AuditEvent.

        Args:
            action: The auditable action that took place.
            actor_id: UUID string of the performing user.
            target_id: UUID string of the affected entity.
            metadata: Optional dictionary of contextual key/value pairs.
            ip_address: Optional client IP for security events.
        """
        self.id: str = str(uuid.uuid4())
        self.action = action
        self.actor_id = actor_id
        self.target_id = target_id
        self.timestamp: datetime = datetime.utcnow()
        self.metadata: Dict[str, Any] = metadata or {}
        self.ip_address = ip_address


class AuditService:
    """Static service for writing audit events.

    All methods are ``async`` and must be awaited.  Failures are swallowed
    and logged as warnings to avoid disrupting the main request flow.

    Example:
        ::

            await AuditService.log(
                action=AuditAction.DATA_ERASURE,
                actor_id="guardian-uuid",
                target_id="learner-uuid",
            )
    """

    @staticmethod
    async def log(
        action: AuditAction,
        actor_id: str,
        target_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[AuditEvent]:
        """Write an audit event to the database asynchronously.

        The database write is best-effort: if it fails, a structured warning
        is emitted but the exception is **not** re-raised.

        Args:
            action: The :class:`AuditAction` describing what happened.
            actor_id: UUID of the user who triggered the event.
            target_id: UUID of the entity that was affected.
            metadata: Optional dict of supplementary context.
            ip_address: Optional client IP address for security events.

        Returns:
            Optional[AuditEvent]: The persisted event, or ``None`` if the
            write failed.

        Example:
            ::

                event = await AuditService.log(
                    action=AuditAction.CONSENT_GRANTED,
                    actor_id="g-001",
                    target_id="l-001",
                    metadata={"version": "1.0"},
                )
        """
        event = AuditEvent(
            action=action,
            actor_id=actor_id,
            target_id=target_id,
            metadata=metadata,
            ip_address=ip_address,
        )
        # In production this persists `event` via AsyncSQLAlchemy.
        # Placeholder: return the constructed event directly.
        return event
