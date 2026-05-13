"""
app/core/cookies.py
---------------------
Secure cookie helpers for EduBoost SA V2.

Implements §3.4:
  - HttpOnly, Secure (prod), SameSite, correct domain/path (P0)
  - No refresh token is JS-readable (P0)
  - Cookie strategy documented in-module (P1)
"""

from __future__ import annotations

import os

from fastapi import Response

# ---------------------------------------------------------------------------
# Cookie strategy (§3.4 P1)
# ---------------------------------------------------------------------------
# The refresh token is stored in an HttpOnly, Secure, SameSite=Lax cookie.
# It is never exposed to JavaScript.
#
# The access token is NOT stored in a cookie by default — the frontend holds
# it in memory (not localStorage / sessionStorage) for the duration of the
# session.  This avoids CSRF risk for the access token while keeping XSS
# exposure minimal.  See docs/security/cookie_strategy.md for full rationale.
#
# Per-environment overrides
#   COOKIE_DOMAIN   — set in production to ".eduboost.co.za"
#   COOKIE_SECURE   — defaults True; set to "false" only in local dev
#   COOKIE_SAMESITE — "lax" (default) or "strict"

REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/auth"          # scope to auth endpoints only (§3.4 P0)
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN") or None          # None = current domain
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() != "false"
COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")  # "lax" | "strict" | "none"

REFRESH_TOKEN_MAX_AGE_SECONDS = 7 * 24 * 3600  # mirrors REFRESH_TOKEN_TTL_DAYS


def set_refresh_cookie(response: Response, raw_refresh_token: str) -> None:
    """Attach the refresh token as an HttpOnly cookie on *response*.

    §3.4 P0 requirements:
      - HttpOnly  ✓ (never JS-readable)
      - Secure    ✓ (env-configurable; True in prod)
      - SameSite  ✓ (env-configurable; 'lax' default)
      - Domain    ✓ (env-configurable; scoped to deployment domain)
      - Path      ✓ (/api/auth — not broadcast to all routes)
    """
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=raw_refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path=COOKIE_PATH,
        max_age=REFRESH_TOKEN_MAX_AGE_SECONDS,
    )


def clear_refresh_cookie(response: Response) -> None:
    """Clear the refresh token cookie on logout (§3.1 P0)."""
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path=COOKIE_PATH,
    )


def get_cookie_policy_summary() -> dict[str, object]:
    """Return current cookie policy as a dict (used in tests and docs)."""
    return {
        "cookie_name": REFRESH_TOKEN_COOKIE_NAME,
        "http_only": True,
        "secure": COOKIE_SECURE,
        "same_site": COOKIE_SAMESITE,
        "domain": COOKIE_DOMAIN,
        "path": COOKIE_PATH,
        "max_age_seconds": REFRESH_TOKEN_MAX_AGE_SECONDS,
        "js_readable": False,
    }
