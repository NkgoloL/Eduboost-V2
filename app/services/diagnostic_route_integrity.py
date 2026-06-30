from __future__ import annotations

from typing import Any

from app.services.diagnostic_data_integrity import DiagnosticIntegrityError
from app.services.diagnostic_session_integrity import validate_session_served_item_binding


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


def snapshot_caps_ref(snapshot: Any) -> str | None:
    value = _attr_or_key(snapshot, "caps_ref", "capsRef", "caps_code", "capsCode")
    return str(value) if value is not None else None


def assert_caps_ref_matches_session(*, submitted_caps_ref: Any | None, session_caps_ref: Any | None) -> None:
    if submitted_caps_ref is None or session_caps_ref is None:
        return
    if str(submitted_caps_ref) != str(session_caps_ref):
        raise DiagnosticIntegrityError(
            f"Diagnostic CAPS reference {submitted_caps_ref!r} does not match session CAPS reference {session_caps_ref!r}"
        )


def served_items_from_snapshot(snapshot: Any, *, session_id: Any) -> list[dict[str, Any]]:
    served_ids = _attr_or_key(snapshot, "served_item_ids", "servedItemIds", "served_items", "servedItems") or []
    caps_ref = snapshot_caps_ref(snapshot)
    return [
        {
            "item_id": item_id,
            "session_id": str(session_id),
            "caps_code": caps_ref,
        }
        for item_id in served_ids
    ]


def validate_adaptive_diagnostic_response(payload: Any, *, snapshot: Any, session_id: Any) -> None:
    """Validate adaptive diagnostic response against recovered session state.

    The adaptive response route receives a single item response. The item must
    be one of the items actually served to the recovered session, and any
    supplied CAPS reference must match the recovered session CAPS reference.
    """
    session_caps_ref = snapshot_caps_ref(snapshot)
    submitted_caps_ref = _attr_or_key(payload, "caps_ref", "capsRef", "caps_code", "capsCode")
    assert_caps_ref_matches_session(submitted_caps_ref=submitted_caps_ref, session_caps_ref=session_caps_ref)

    served_items = served_items_from_snapshot(snapshot, session_id=session_id)
    if not served_items:
        raise DiagnosticIntegrityError("Diagnostic session has no served items recorded")

    validate_session_served_item_binding(
        payload,
        served_items=served_items,
        session_id=session_id,
        caps_code=session_caps_ref,
    )


__all__ = [
    "assert_caps_ref_matches_session",
    "served_items_from_snapshot",
    "snapshot_caps_ref",
    "validate_adaptive_diagnostic_response",
]
