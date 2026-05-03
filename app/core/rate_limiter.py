"""Redis-backed AI quota controls."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis import increment_counter


@dataclass(slots=True)
class QuotaDecision:
    key: str
    used: int
    limit: int
    retry_after: int


class AIQuotaExceeded(HTTPException):
    def __init__(self, decision: QuotaDecision) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI quota of {decision.limit} requests exceeded",
            headers={"Retry-After": str(decision.retry_after)},
        )


def seconds_until_tomorrow(now: datetime | None = None) -> int:
    current = now or datetime.now(UTC)
    tomorrow = (current + timedelta(days=1)).date()
    boundary = datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=UTC)
    return max(1, int((boundary - current).total_seconds()))


async def check_ai_quota(user_id: str, tier: str = "free") -> QuotaDecision:
    """Consume one AI request and raise `AIQuotaExceeded` when free quota is exhausted."""
    if tier == "premium":
        return QuotaDecision(key="", used=0, limit=settings.PREMIUM_DAILY_REQUEST_QUOTA, retry_after=0)

    today = datetime.now(UTC).date().isoformat()
    retry_after = seconds_until_tomorrow()
    key = f"ai_quota:{user_id}:{today}"
    used = await increment_counter(key, ttl_seconds=24 * 3600)
    decision = QuotaDecision(key=key, used=used, limit=settings.FREE_DAILY_REQUEST_QUOTA, retry_after=retry_after)
    if used > decision.limit:
        raise AIQuotaExceeded(decision)
    return decision
