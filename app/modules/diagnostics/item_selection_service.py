from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.modules.diagnostics.irt_engine import fisher_information_3pl


@dataclass(frozen=True)
class SelectionResult:
    item: object | None
    information: float
    eligible_count: int


class ItemSelectionService:
    """Maximum Fisher Information item selection with exposure filtering."""

    def select_max_information_item(
        self,
        items: Iterable[object],
        *,
        theta: float,
        served_ids: set[str] | set[object] | None = None,
    ) -> SelectionResult:
        served = {str(value) for value in (served_ids or set())}
        best_item = None
        best_information = -1.0
        eligible_count = 0
        for item in items:
            item_id = str(getattr(item, "item_id", getattr(item, "id", "")))
            if item_id in served:
                continue
            if not self._is_eligible(item):
                continue
            eligible_count += 1
            info = fisher_information_3pl(
                theta,
                float(getattr(item, "discrimination_a", getattr(item, "a_param", 1.0)) or 1.0),
                float(getattr(item, "difficulty_b", getattr(item, "b_param", 0.0)) or 0.0),
                float(getattr(item, "guessing_c", 0.25) or 0.25),
            )
            if info > best_information:
                best_item = item
                best_information = info
        return SelectionResult(best_item, max(best_information, 0.0), eligible_count)

    @staticmethod
    def _is_eligible(item: object) -> bool:
        status = getattr(item, "review_status", "approved")
        status = getattr(status, "value", status)
        exposure_count = int(getattr(item, "exposure_count", 0) or 0)
        max_exposure = int(getattr(item, "max_exposure", 50) or 50)
        safety_passed = bool(getattr(item, "safety_passed", True))
        return status == "approved" and safety_passed and exposure_count < max_exposure
