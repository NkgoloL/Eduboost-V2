"""AI Generation Budget & Cost Kill-Switch Guard (TSR-11.11).

Tracks and bounds per-request and per-day token usage to prevent
runaway LLM vendor API costs.
"""
from __future__ import annotations

from typing import Any
from fastapi import HTTPException, status

DEFAULT_MAX_TOKENS_PER_REQUEST = 4096
DEFAULT_DAILY_TOKEN_BUDGET = 500000


class AIBudgetExceededError(HTTPException):
    def __init__(self, detail: str = "AI generation request exceeded approved token/cost budget."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "3600", "X-AI-Budget-Status": "EXCEEDED"},
        )


class AIBudgetGuard:
    """Enforces token budget reservations and emergency cost kill-switches."""

    def __init__(
        self,
        max_tokens_per_request: int = DEFAULT_MAX_TOKENS_PER_REQUEST,
        daily_budget: int = DEFAULT_DAILY_TOKEN_BUDGET,
    ) -> None:
        self.max_tokens_per_request = max_tokens_per_request
        self.daily_budget = daily_budget
        self._current_usage = 0

    def check_and_reserve(self, estimated_tokens: int) -> int:
        """Reserve tokens against the active budget; raise 429 if exceeded."""
        if estimated_tokens <= 0:
            raise ValueError("Estimated tokens must be positive.")

        if estimated_tokens > self.max_tokens_per_request:
            raise AIBudgetExceededError(
                f"Request tokens ({estimated_tokens}) exceed maximum single-request limit ({self.max_tokens_per_request})."
            )

        if self._current_usage + estimated_tokens > self.daily_budget:
            raise AIBudgetExceededError(
                f"Daily AI budget exhausted ({self._current_usage}/{self.daily_budget} tokens used)."
            )

        self._current_usage += estimated_tokens
        return self._current_usage

    def reset_usage(self) -> None:
        """Reset the active budget counter."""
        self._current_usage = 0
