"""Compatibility helpers for audit repository consolidation.

This module intentionally does not choose a persistence backend. It adapts
legacy audit call shapes into a canonical event dictionary so call sites can be
migrated safely before deleting older repositories.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Protocol


class SupportsAuditRecord(Protocol):
    def record(self, **kwargs: Any) -> Any: ...


class SupportsAuditAppend(Protocol):
    def append(self, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class AuditEventInput:
    action: str
    actor_id: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    learner_id: str | None = None
    learner_pseudonym: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_canonical_payload(self) -> dict[str, Any]:
        payload = dict(self.metadata)
        if self.learner_id is not None:
            payload.setdefault("learner_id", self.learner_id)
        if self.learner_pseudonym is not None:
            payload.setdefault("learner_pseudonym", self.learner_pseudonym)
        return {
            "action": self.action,
            "actor_id": self.actor_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id or self.learner_id or self.learner_pseudonym,
            "payload": payload,
        }


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


class AuditRepositoryCompatAdapter:
    """Adapter that supports legacy append-style calls and canonical record calls.

    Preferred repository method order:
    1. record(**canonical_event)
    2. append(**canonical_event)
    3. create(**canonical_event)

    The adapter is deliberately small and testable. It lets future batches
    migrate call sites one at a time without losing audit coverage.
    """

    def __init__(self, repository: Any):
        self.repository = repository

    async def record(self, event: AuditEventInput | None = None, **kwargs: Any) -> Any:
        audit_input = event or normalize_audit_kwargs(**kwargs)
        canonical = audit_input.to_canonical_payload()

        if hasattr(self.repository, "record"):
            return await _maybe_await(self.repository.record(**canonical))
        if hasattr(self.repository, "append"):
            return await _maybe_await(self.repository.append(**canonical))
        if hasattr(self.repository, "create"):
            return await _maybe_await(self.repository.create(**canonical))

        raise TypeError(
            "Audit repository must expose record(**event), append(**event), or create(**event)"
        )

    async def append(self, **kwargs: Any) -> Any:
        return await self.record(**kwargs)


def normalize_audit_kwargs(**kwargs: Any) -> AuditEventInput:
    """Normalize legacy audit keyword shapes into AuditEventInput."""
    action = (
        kwargs.pop("action", None)
        or kwargs.pop("event_type", None)
        or kwargs.pop("event", None)
        or kwargs.pop("operation", None)
    )
    if not action:
        raise ValueError("audit event requires action/event_type/event/operation")

    metadata = kwargs.pop("metadata", None) or kwargs.pop("payload", None) or {}
    if not isinstance(metadata, dict):
        metadata = {"value": metadata}

    known = {
        "actor_id",
        "resource_type",
        "resource_id",
        "learner_id",
        "learner_pseudonym",
    }
    extras = {key: kwargs.pop(key) for key in list(kwargs) if key not in known}
    metadata.update(extras)

    return AuditEventInput(
        action=str(action),
        actor_id=kwargs.pop("actor_id", None),
        resource_type=kwargs.pop("resource_type", None),
        resource_id=kwargs.pop("resource_id", None),
        learner_id=kwargs.pop("learner_id", None),
        learner_pseudonym=kwargs.pop("learner_pseudonym", None),
        metadata=metadata,
    )


__all__ = [
    "AuditEventInput",
    "AuditRepositoryCompatAdapter",
    "normalize_audit_kwargs",
]
