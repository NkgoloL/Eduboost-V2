from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass, field
from typing import Any


CONSENT_SERVICE_CANDIDATES = (
    "app.services.consent_service.ConsentService",
    "app.modules.consent.service.ConsentService",
)

POPIA_SERVICE_CANDIDATES = (
    "app.services.popia_service.POPIADataRightsService",
)


@dataclass(frozen=True)
class ConstructorProbe:
    target: str
    importable: bool
    class_found: bool
    constructor_signature: str
    required_parameters: tuple[str, ...]
    error: str | None = None


@dataclass(frozen=True)
class ConsentRuntimeOperation:
    action: str
    actor_id: str
    learner_id: str
    operation_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_audit_event(self) -> dict[str, Any]:
        payload = dict(self.metadata)
        payload.setdefault("learner_id", self.learner_id)
        payload.setdefault("operation_type", self.operation_type)
        return {
            "action": self.action,
            "actor_id": self.actor_id,
            "resource_type": "learner_consent",
            "resource_id": self.learner_id,
            "metadata": payload,
        }


def _split_target(target: str) -> tuple[str, str]:
    module_name, class_name = target.rsplit(".", 1)
    return module_name, class_name


def probe_constructor(target: str) -> ConstructorProbe:
    module_name, class_name = _split_target(target)
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return ConstructorProbe(
            target=target,
            importable=False,
            class_found=False,
            constructor_signature="",
            required_parameters=(),
            error=f"{type(exc).__name__}: {exc}",
        )

    cls = getattr(module, class_name, None)
    if cls is None:
        return ConstructorProbe(
            target=target,
            importable=True,
            class_found=False,
            constructor_signature="",
            required_parameters=(),
            error=f"{class_name} not found",
        )

    try:
        signature = inspect.signature(cls)
    except Exception:
        signature = inspect.signature(cls.__init__)

    required = []
    for name, param in signature.parameters.items():
        if name == "self":
            continue
        if param.default is inspect.Parameter.empty and param.kind in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }:
            required.append(name)

    return ConstructorProbe(
        target=target,
        importable=True,
        class_found=True,
        constructor_signature=str(signature),
        required_parameters=tuple(required),
        error=None,
    )


def probe_known_consent_surfaces() -> list[ConstructorProbe]:
    return [probe_constructor(target) for target in (*CONSENT_SERVICE_CANDIDATES, *POPIA_SERVICE_CANDIDATES)]


def normalize_consent_runtime_operation(
    *,
    action: str,
    actor_id: str,
    learner_id: str,
    operation_type: str | None = None,
    metadata: dict[str, Any] | None = None,
    **extra: Any,
) -> ConsentRuntimeOperation:
    if not action:
        raise ValueError("action is required")
    if not actor_id:
        raise ValueError("actor_id is required")
    if not learner_id:
        raise ValueError("learner_id is required")

    resolved_operation_type = operation_type
    if resolved_operation_type is None:
        if action.endswith(".read"):
            resolved_operation_type = "read"
        elif any(token in action for token in (".grant", ".granted", ".revoke", ".revoked", ".request", ".cancel")):
            resolved_operation_type = "write"
        else:
            resolved_operation_type = "unknown"

    merged_metadata = dict(metadata or {})
    merged_metadata.update(extra)

    return ConsentRuntimeOperation(
        action=action,
        actor_id=actor_id,
        learner_id=learner_id,
        operation_type=resolved_operation_type,
        metadata=merged_metadata,
    )


__all__ = [
    "CONSENT_SERVICE_CANDIDATES",
    "POPIA_SERVICE_CANDIDATES",
    "ConstructorProbe",
    "ConsentRuntimeOperation",
    "normalize_consent_runtime_operation",
    "probe_constructor",
    "probe_known_consent_surfaces",
]
