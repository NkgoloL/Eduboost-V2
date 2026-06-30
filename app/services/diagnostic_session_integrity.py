from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.diagnostic_data_integrity import (
    DiagnosticIntegrityError,
    extract_diagnostic_item_ids,
    validate_diagnostic_submission_payload,
)


@dataclass(frozen=True)
class ServedDiagnosticItem:
    item_id: Any
    session_id: Any | None = None
    caps_topic: str | None = None
    caps_code: str | None = None


def _attr_or_key(value: Any, *names: str) -> Any:
    if isinstance(value, dict):
        for name in names:
            if value.get(name) is not None:
                return value[name]
    for name in names:
        item = getattr(value, name, None)
        if item is not None:
            return item
    return None


def normalize_served_item(value: Any) -> ServedDiagnosticItem:
    return ServedDiagnosticItem(
        item_id=_attr_or_key(value, "item_id", "itemId", "diagnostic_item_id", "question_id", "id"),
        session_id=_attr_or_key(value, "session_id", "sessionId", "diagnostic_session_id"),
        caps_topic=_attr_or_key(value, "caps_topic", "capsTopic", "topic"),
        caps_code=_attr_or_key(value, "caps_code", "capsCode", "caps"),
    )


def served_item_ids(served_items: list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any]) -> set[Any]:
    ids: set[Any] = set()
    for item in served_items:
        normalized = normalize_served_item(item)
        if normalized.item_id is not None:
            ids.add(normalized.item_id)
    return ids


def validate_session_served_item_binding(
    payload: Any,
    *,
    served_items: list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any],
    session_id: Any | None = None,
    caps_topic: str | None = None,
    caps_code: str | None = None,
) -> None:
    """Validate submitted diagnostic item IDs against served session items.

    This accepts DB rows, ORM rows, dictionaries, or DTOs. It proves the
    integrity rule independently from any one repository implementation.
    """
    normalized = [normalize_served_item(item) for item in served_items]
    item_ids = {item.item_id for item in normalized if item.item_id is not None}

    validate_diagnostic_submission_payload(payload, served_item_ids=item_ids, require_items=True)

    submitted_ids = {str(item_id) for item_id in extract_diagnostic_item_ids(payload)}

    for item in normalized:
        if str(item.item_id) not in submitted_ids:
            continue

        if session_id is not None and item.session_id is not None and str(item.session_id) != str(session_id):
            raise DiagnosticIntegrityError(
                f"Diagnostic item {item.item_id!r} belongs to session {item.session_id!r}, not {session_id!r}"
            )

        if caps_topic is not None and item.caps_topic is not None and str(item.caps_topic) != str(caps_topic):
            raise DiagnosticIntegrityError(
                f"Diagnostic item {item.item_id!r} belongs to CAPS topic {item.caps_topic!r}, not {caps_topic!r}"
            )

        if caps_code is not None and item.caps_code is not None and str(item.caps_code) != str(caps_code):
            raise DiagnosticIntegrityError(
                f"Diagnostic item {item.item_id!r} belongs to CAPS code {item.caps_code!r}, not {caps_code!r}"
            )


__all__ = [
    "ServedDiagnosticItem",
    "normalize_served_item",
    "served_item_ids",
    "validate_session_served_item_binding",
]
