"""Compatibility helpers for consent service consolidation.

⚠️ DEPRECATION NOTICE:
This module is a legacy compatibility shim. The canonical consent lifecycle services are:
    - app.services.consent_service.ConsentService
    - app.services.popia_service.POPIADataRightsService
DO NOT use this module for new v2 routes or features.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any

warnings.warn(
    "app.services.consent_compat is deprecated; use app.services.consent_service instead.",
    DeprecationWarning,
    stacklevel=2,
)


READ_CONSENT_ACTIONS = {
    "consent.status.read",
    "consent.export.read",
    "consent.audit.read",
}

WRITE_CONSENT_ACTIONS = {
    "consent.granted",
    "consent.revoked",
    "consent.renewed",
    "consent.restricted",
    "consent.erasure.requested",
    "consent.erasure.cancelled",
}


@dataclass(frozen=True)
class ConsentAuditEvent:
    action: str
    actor_id: str
    learner_id: str
    resource_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_audit_kwargs(self) -> dict[str, Any]:
        payload = dict(self.metadata)
        payload.setdefault("learner_id", self.learner_id)
        return {
            "action": self.action,
            "actor_id": self.actor_id,
            "resource_type": "learner_consent",
            "resource_id": self.resource_id or self.learner_id,
            "metadata": payload,
        }


def normalize_consent_audit_event(
    *,
    action: str,
    actor_id: str,
    learner_id: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    **extra: Any,
) -> ConsentAuditEvent:
    """Normalize consent audit inputs into an audit-compatible event.

    Future batches should use this as the edge-normalizer while migrating split
    consent services/repositories toward one canonical path.
    """
    if not action:
        raise ValueError("consent audit action is required")
    if not actor_id:
        raise ValueError("consent audit actor_id is required")

    resolved_learner_id = learner_id or resource_id
    if not resolved_learner_id:
        raise ValueError("consent audit learner_id or resource_id is required")

    merged_metadata = dict(metadata or {})
    merged_metadata.update(extra)

    return ConsentAuditEvent(
        action=action,
        actor_id=actor_id,
        learner_id=resolved_learner_id,
        resource_id=resource_id,
        metadata=merged_metadata,
    )


def classify_consent_action(action: str) -> str:
    if action in READ_CONSENT_ACTIONS:
        return "read"
    if action in WRITE_CONSENT_ACTIONS:
        return "write"
    return "unknown"


__all__ = [
    "ConsentAuditEvent",
    "READ_CONSENT_ACTIONS",
    "WRITE_CONSENT_ACTIONS",
    "classify_consent_action",
    "normalize_consent_audit_event",
]
