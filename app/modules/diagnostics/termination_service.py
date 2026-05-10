from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TerminationDecision:
    should_stop: bool
    reason: str | None = None


class TerminationService:
    """Diagnostic stopping criteria from the diagnostics assessment roadmap."""

    def __init__(self, target_se: float = 0.40, max_items: int = 15, min_pool: int = 3) -> None:
        self.target_se = target_se
        self.max_items = max_items
        self.min_pool = min_pool

    def evaluate(self, *, standard_error: float, items_served: int, pool_size: int) -> TerminationDecision:
        if standard_error <= self.target_se:
            return TerminationDecision(True, "se_converged")
        if items_served >= self.max_items:
            return TerminationDecision(True, "max_items_served")
        if pool_size < self.min_pool:
            return TerminationDecision(True, "item_pool_exhausted")
        return TerminationDecision(False, None)
