from __future__ import annotations

from types import SimpleNamespace
from typing import Any


SCORING_PARAMETER_FIELDS = (
    "discrimination_a",
    "difficulty_b",
    "guessing_c",
    "a_param",
    "b_param",
    "caps_ref",
    "misconception_tags",
)


def _value(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def diagnostic_response_snapshot(item: Any, *, item_id: str) -> dict[str, Any]:
    """Persist immutable scoring context for a diagnostic response."""
    discrimination = _value(item, "discrimination_a", _value(item, "a_param", 1.0))
    difficulty = _value(item, "difficulty_b", _value(item, "b_param", 0.0))
    guessing = _value(item, "guessing_c", 0.25)
    caps_ref = _value(item, "caps_ref", None)
    misconception_tags = list(_value(item, "misconception_tags", []) or [])

    return {
        "item_id": str(item_id),
        "scoring": {
            "item_id": str(item_id),
            "discrimination_a": float(discrimination or 1.0),
            "difficulty_b": float(difficulty or 0.0),
            "guessing_c": float(guessing or 0.25),
            "a_param": float(discrimination or 1.0),
            "b_param": float(difficulty or 0.0),
            "caps_ref": caps_ref,
            "misconception_tags": misconception_tags,
        },
    }


def diagnostic_item_from_response(row: dict[str, Any], *, fallback_item: Any | None = None) -> Any:
    """Rebuild the item object used for historical IRT scoring.

    New snapshots carry a `scoring` object. Legacy snapshots may not. Legacy
    fallback is retained for backwards compatibility, but new responses must not
    recalculate all historical rows with the current item object.
    """
    scoring = row.get("scoring") or row.get("item")
    if isinstance(scoring, dict) and scoring:
        return SimpleNamespace(**scoring)

    if fallback_item is not None:
        item_id = str(row.get("item_id") or _value(fallback_item, "item_id", _value(fallback_item, "id", "")))
        return SimpleNamespace(**diagnostic_response_snapshot(fallback_item, item_id=item_id)["scoring"])

    return SimpleNamespace(
        item_id=str(row.get("item_id", "")),
        discrimination_a=1.0,
        difficulty_b=0.0,
        guessing_c=0.25,
        a_param=1.0,
        b_param=0.0,
        caps_ref=row.get("caps_ref"),
        misconception_tags=[],
    )


__all__ = ["SCORING_PARAMETER_FIELDS", "diagnostic_item_from_response", "diagnostic_response_snapshot"]
