"""Runtime-safe helpers for backend consolidation implementation.

These helpers provide stable, testable seams for the first implementation phase.
They do not delete legacy paths or choose a database migration strategy.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

from app.repositories.audit_compat import AuditRepositoryCompatAdapter, normalize_audit_kwargs
from app.services.consent_compat import normalize_consent_audit_event


@dataclass(frozen=True)
class CanonicalAuditWrite:
    action: str
    actor_id: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_kwargs(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "actor_id": self.actor_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "metadata": dict(self.metadata),
        }


async def record_canonical_audit_event(repository: Any, event: CanonicalAuditWrite | dict[str, Any]) -> Any:
    """Record a canonical audit event through the compatibility adapter."""
    adapter = AuditRepositoryCompatAdapter(repository)
    if isinstance(event, CanonicalAuditWrite):
        return await adapter.record(**event.to_kwargs())
    return await adapter.record(**event)


async def record_consent_audit_event(
    repository: Any,
    *,
    action: str,
    actor_id: str,
    learner_id: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    **extra: Any,
) -> Any:
    """Normalize a consent event and record it through the audit adapter."""
    consent_event = normalize_consent_audit_event(
        action=action,
        actor_id=actor_id,
        learner_id=learner_id,
        resource_id=resource_id,
        metadata=metadata,
        **extra,
    )
    return await record_canonical_audit_event(repository, consent_event.to_audit_kwargs())


@dataclass(frozen=True)
class ConstructorProbeResult:
    import_path: str
    class_name: str
    importable: bool
    constructable_without_args: bool
    signature: str
    error: str | None = None


def probe_constructor(import_path: str, class_name: str) -> ConstructorProbeResult:
    """Inspect whether a service class is importable and no-arg constructable."""
    try:
        module = __import__(import_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        signature = str(inspect.signature(cls))
        try:
            cls()
            constructable = True
            error = None
        except Exception as exc:  # diagnostics only
            constructable = False
            error = f"{type(exc).__name__}: {exc}"
        return ConstructorProbeResult(
            import_path=import_path,
            class_name=class_name,
            importable=True,
            constructable_without_args=constructable,
            signature=signature,
            error=error,
        )
    except Exception as exc:
        return ConstructorProbeResult(
            import_path=import_path,
            class_name=class_name,
            importable=False,
            constructable_without_args=False,
            signature="",
            error=f"{type(exc).__name__}: {exc}",
        )


def normalize_legacy_audit_call(**kwargs: Any) -> dict[str, Any]:
    """Expose legacy audit normalization as an implementation-facing helper."""
    return normalize_audit_kwargs(**kwargs).to_canonical_payload()


__all__ = [
    "CanonicalAuditWrite",
    "ConstructorProbeResult",
    "normalize_legacy_audit_call",
    "probe_constructor",
    "record_canonical_audit_event",
    "record_consent_audit_event",
]
