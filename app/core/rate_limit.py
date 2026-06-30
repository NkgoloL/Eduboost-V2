"""
app/middleware/rate_limit.py
-----------------------------
Rate limiting for EduBoost SA V2 — implements §3.7.

Uses slowapi (Starlette-native limiter backed by Redis).
All P0 endpoints are explicitly limited; P1 account and IP throttling
are implemented as reusable dependencies.

Usage in api_v2.py
-------------------
    from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

Usage in routers
-----------------
    from app.middleware.rate_limit import limiter
    from fastapi import Request

    @router.post("/login")
    @limiter.limit(LOGIN_LIMIT)
    async def login(request: Request, ...):
        ...
"""

from __future__ import annotations

import os

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# ---------------------------------------------------------------------------
# Limit strings (§3.7 P0)
# Override via environment variables for tuning without code changes.
# ---------------------------------------------------------------------------

LOGIN_LIMIT: str = os.getenv("RATE_LOGIN", "10/minute")
SIGNUP_LIMIT: str = os.getenv("RATE_SIGNUP", "5/minute")
REFRESH_LIMIT: str = os.getenv("RATE_REFRESH", "30/minute")
PASSWORD_RESET_LIMIT: str = os.getenv("RATE_PASSWORD_RESET", "5/minute")
EMAIL_VERIFY_LIMIT: str = os.getenv("RATE_EMAIL_VERIFY", "10/minute")
LLM_LESSON_LIMIT: str = os.getenv("RATE_LLM_LESSON", "20/minute")
DATA_EXPORT_LIMIT: str = os.getenv("RATE_DATA_EXPORT", "5/hour")
BILLING_WEBHOOK_LIMIT: str = os.getenv("RATE_BILLING_WEBHOOK", "60/minute")

# P1 — account-level throttling (applied by user_id, not IP)
ACCOUNT_DEFAULT_LIMIT: str = os.getenv("RATE_ACCOUNT_DEFAULT", "200/minute")

# P1 — IP-level throttling (broad envelope)
IP_DEFAULT_LIMIT: str = os.getenv("RATE_IP_DEFAULT", "500/minute")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ---------------------------------------------------------------------------
# Limiter instances
# ---------------------------------------------------------------------------

# IP-based limiter (default key func = remote address)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    default_limits=[IP_DEFAULT_LIMIT],
)


def _get_account_key(request: Request) -> str:
    """Key function for account-level throttling.

    Extracts user_id from the resolved token claims attached by the auth
    dependency.  Falls back to IP if not authenticated.
    """
    user = getattr(request.state, "current_user", None)
    if user and hasattr(user, "user_id"):
        return f"account:{user.user_id}"
    return get_remote_address(request)


account_limiter = Limiter(
    key_func=_get_account_key,
    storage_uri=REDIS_URL,
    default_limits=[ACCOUNT_DEFAULT_LIMIT],
)


# ---------------------------------------------------------------------------
# P1 — Risk-based throttling helper
# ---------------------------------------------------------------------------
# Routers import and apply this after detecting suspicious patterns
# (multiple failed logins, unusual request pattern).

_RISK_PENALTY_LIMIT = "3/minute"


def risk_limit(request: Request) -> str:
    """Return a tighter rate-limit string for requests flagged as risky.

    Wire this into services that track failed-auth counts.
    """
    failed_count = getattr(request.state, "failed_auth_count", 0)
    return _RISK_PENALTY_LIMIT if failed_count >= 3 else LOGIN_LIMIT


# ---------------------------------------------------------------------------
# Exception handler
# ---------------------------------------------------------------------------

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please slow down and try again shortly.",
            "limit": str(exc.detail),
        },
        headers={"Retry-After": "60"},
    )
