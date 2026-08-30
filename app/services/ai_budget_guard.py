from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, ClassVar
import threading
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
    """Enforces token budget reservations and emergency cost kill-switches.

    Supports multi-process and worker replica coordination via day-keyed shared state
    and Redis atomic operations when available.
    """

    _SHARED_USAGE: ClassVar[dict[str, int]] = {}
    _LOCK: ClassVar[threading.Lock] = threading.Lock()

    def __init__(
        self,
        max_tokens_per_request: int = DEFAULT_MAX_TOKENS_PER_REQUEST,
        daily_budget: int = DEFAULT_DAILY_TOKEN_BUDGET,
        redis_client: Any | None = None,
    ) -> None:
        self.max_tokens_per_request = max_tokens_per_request
        self.daily_budget = daily_budget
        self.redis_client = redis_client

    @staticmethod
    def _current_day_key() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @property
    def _current_usage(self) -> int:
        day_key = self._current_day_key()
        with self._LOCK:
            return self._SHARED_USAGE.get(day_key, 0)

    @_current_usage.setter
    def _current_usage(self, val: int) -> None:
        day_key = self._current_day_key()
        with self._LOCK:
            self._SHARED_USAGE[day_key] = val

    def check_and_reserve(self, estimated_tokens: int) -> int:
        """Reserve tokens against the active day budget; raise 429 if exceeded."""
        if estimated_tokens <= 0:
            raise ValueError("Estimated tokens must be positive.")

        if estimated_tokens > self.max_tokens_per_request:
            raise AIBudgetExceededError(
                f"Request tokens ({estimated_tokens}) exceed maximum single-request limit ({self.max_tokens_per_request})."
            )

        day_key = self._current_day_key()
        with self._LOCK:
            current = self._SHARED_USAGE.get(day_key, 0)
            if current + estimated_tokens > self.daily_budget:
                raise AIBudgetExceededError(
                    f"Daily AI budget exhausted ({current}/{self.daily_budget} tokens used)."
                )
            self._SHARED_USAGE[day_key] = current + estimated_tokens
            return self._SHARED_USAGE[day_key]

    async def check_and_reserve_async(self, estimated_tokens: int) -> int:
        """Async reservation supporting atomic Redis increment when configured."""
        if estimated_tokens <= 0:
            raise ValueError("Estimated tokens must be positive.")

        if estimated_tokens > self.max_tokens_per_request:
            raise AIBudgetExceededError(
                f"Request tokens ({estimated_tokens}) exceed maximum single-request limit ({self.max_tokens_per_request})."
            )

        if self.redis_client:
            day_key = f"ai_budget:daily:{self._current_day_key()}"
            try:
                current = await self.redis_client.incrby(day_key, estimated_tokens)
                if current == estimated_tokens:
                    await self.redis_client.expire(day_key, 86400)
                if current > self.daily_budget:
                    await self.redis_client.decrby(day_key, estimated_tokens)
                    raise AIBudgetExceededError(
                        f"Daily AI budget exhausted ({current - estimated_tokens}/{self.daily_budget} tokens used)."
                    )
                return current
            except AIBudgetExceededError:
                raise
            except Exception:
                # Fall back to shared in-process reservation
                pass

        return self.check_and_reserve(estimated_tokens)

    def reset_usage(self) -> None:
        """Reset the active day budget counter."""
        day_key = self._current_day_key()
        with self._LOCK:
            self._SHARED_USAGE[day_key] = 0


_DEFAULT_GUARD: AIBudgetGuard | None = None


def get_ai_budget_guard(redis_client: Any | None = None) -> AIBudgetGuard:
    """Retrieve the singleton AI budget guard for runtime requests."""
    global _DEFAULT_GUARD
    if _DEFAULT_GUARD is None:
        client = redis_client
        if client is None:
            try:
                from app.core.redis import get_redis
                client = get_redis()
            except Exception:
                client = None
        _DEFAULT_GUARD = AIBudgetGuard(redis_client=client)
    elif redis_client is not None:
        _DEFAULT_GUARD.redis_client = redis_client
    return _DEFAULT_GUARD


