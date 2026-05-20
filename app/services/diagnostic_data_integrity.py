from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


class DiagnosticIntegrityError(ValueError):
    """Raised when a diagnostic submission or mastery update is unsafe."""


@dataclass(frozen=True)
class DiagnosticSubmissionIntegrityResult:
    item_ids: tuple[Any, ...]
    duplicate_item_ids: tuple[Any, ...]
    unserved_item_ids: tuple[Any, ...]


def extract_diagnostic_item_ids(payload: Any) -> list[Any]:
    """Extract item IDs from dict/Pydantic/dataclass diagnostic payloads."""
    found: list[Any] = []
    seen: set[int] = set()

    def walk(value: Any) -> None:
        if value is None:
            return
        value_identity = id(value)
        if value_identity in seen:
            return
        seen.add(value_identity)

        if isinstance(value, (str, bytes, bytearray)):
            return

        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"item_id", "itemId", "diagnostic_item_id", "question_id", "questionId"} and item is not None:
                    found.append(item)
                else:
                    walk(item)
            return

        for attr in ("item_id", "itemId", "diagnostic_item_id", "question_id", "questionId"):
            item = getattr(value, attr, None)
            if item is not None:
                found.append(item)

        for attr in ("responses", "answers", "items", "events", "payload", "questions"):
            child = getattr(value, attr, None)
            if child is not None:
                walk(child)

        if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray)):
            for item in value:
                walk(item)

    walk(payload)
    return found


def validate_diagnostic_submission_payload(
    payload: Any,
    *,
    served_item_ids: set[Any] | frozenset[Any] | tuple[Any, ...] | list[Any] | None = None,
    require_items: bool = True,
) -> DiagnosticSubmissionIntegrityResult:
    item_ids = extract_diagnostic_item_ids(payload)
    if require_items and not item_ids:
        raise DiagnosticIntegrityError("Diagnostic submission contains no item_id values")

    duplicates: list[Any] = []
    seen: set[str] = set()
    for item_id in item_ids:
        key = str(item_id)
        if key in seen and item_id not in duplicates:
            duplicates.append(item_id)
        seen.add(key)

    if duplicates:
        raise DiagnosticIntegrityError(f"Duplicate diagnostic item responses are not allowed: {duplicates}")

    served = {str(item) for item in served_item_ids or []}
    unserved = [item for item in item_ids if served and str(item) not in served]
    if unserved:
        raise DiagnosticIntegrityError(f"Diagnostic submission includes unserved item IDs: {unserved}")

    return DiagnosticSubmissionIntegrityResult(
        item_ids=tuple(item_ids),
        duplicate_item_ids=tuple(duplicates),
        unserved_item_ids=tuple(unserved),
    )


def _number(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except Exception as exc:
        raise DiagnosticIntegrityError(f"{field_name} must be numeric") from exc
    if not math.isfinite(number):
        raise DiagnosticIntegrityError(f"{field_name} must be finite")
    return number


def validate_theta_update(
    *,
    old_theta: Any,
    new_theta: Any,
    min_theta: float = -4.0,
    max_theta: float = 4.0,
    max_abs_delta: float = 2.5,
) -> float:
    old_value = _number(old_theta, "old_theta")
    new_value = _number(new_theta, "new_theta")
    if new_value < min_theta or new_value > max_theta:
        raise DiagnosticIntegrityError(f"new_theta out of bounds: {new_value}")
    if abs(new_value - old_value) > max_abs_delta:
        raise DiagnosticIntegrityError(f"theta update delta too large: {old_value} -> {new_value}")
    return new_value


def validate_mastery_update_payload(payload: Any) -> None:
    """Validate common mastery/theta update payload shapes."""
    if payload is None:
        return

    if isinstance(payload, dict):
        old_theta = payload.get("old_theta", payload.get("previous_theta", payload.get("theta_before")))
        new_theta = payload.get("new_theta", payload.get("theta", payload.get("theta_after")))
    else:
        old_theta = getattr(payload, "old_theta", getattr(payload, "previous_theta", getattr(payload, "theta_before", None)))
        new_theta = getattr(payload, "new_theta", getattr(payload, "theta", getattr(payload, "theta_after", None)))

    if old_theta is not None and new_theta is not None:
        validate_theta_update(old_theta=old_theta, new_theta=new_theta)


def clamp_theta(value: Any, *, min_theta: float = -4.0, max_theta: float = 4.0) -> float:
    number = _number(value, "theta")
    return max(min_theta, min(max_theta, number))


__all__ = [
    "DiagnosticIntegrityError",
    "DiagnosticSubmissionIntegrityResult",
    "clamp_theta",
    "extract_diagnostic_item_ids",
    "validate_diagnostic_submission_payload",
    "validate_mastery_update_payload",
    "validate_theta_update",
]
