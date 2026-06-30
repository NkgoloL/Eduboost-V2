from __future__ import annotations

from typing import Iterable


class PracticeGenerator:
    """Select adaptive practice items from diagnostic gaps and misconception tags."""

    def select_items(
        self,
        items: Iterable[object],
        *,
        gap_topics: list[str],
        theta: float,
        served_ids: set[str] | None = None,
        per_gap: int = 5,
    ) -> list[object]:
        served = served_ids or set()
        selected: list[object] = []
        for gap in gap_topics:
            candidates = [
                item for item in items
                if getattr(item, "caps_ref", None) == gap
                and str(getattr(item, "item_id", getattr(item, "id", ""))) not in served
                and abs(float(getattr(item, "difficulty_b", getattr(item, "b_param", 0.0)) or 0.0) - theta) <= 0.5
                and getattr(getattr(item, "review_status", "approved"), "value", getattr(item, "review_status", "approved")) == "approved"
            ]
            candidates.sort(key=lambda item: abs(float(getattr(item, "difficulty_b", 0.0) or 0.0) - theta))
            selected.extend(candidates[:per_gap])
        return selected
