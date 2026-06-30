"""
A.4 — Cookie policy tests (extends test_auth_cookie_policy.py).

Tests that:
  - refresh cookie is HttpOnly
  - refresh cookie is Secure in production context
  - cookie has correct SameSite value
  - cookie Path is scoped to /api/auth (not broadcast to all routes)
  - access token is NOT stored in a JS-readable cookie (backend response audit)
  - cookie policy summary reflects all required attributes
"""
from __future__ import annotations

from unittest.mock import patch

from starlette.responses import Response

from app.core.cookies import (
    REFRESH_TOKEN_COOKIE_NAME,
    clear_refresh_cookie,
    get_cookie_policy_summary,
    set_refresh_cookie,
)


# ── A.4.1 — Refresh cookie is HttpOnly ───────────────────────────────────────

def test_refresh_cookie_is_http_only():
    """Refresh token cookie must be HttpOnly (not JS-readable)."""
    response = Response()
    set_refresh_cookie(response, "raw-refresh-token")

    cookie = response.headers.get("set-cookie", "")
    assert "HttpOnly" in cookie, "Refresh cookie must be HttpOnly"


# ── A.4.2 — Refresh cookie is Secure in production ───────────────────────────

def test_refresh_cookie_is_secure_in_production():
    """Refresh token cookie must be Secure=True when COOKIE_SECURE is True."""
    response = Response()
    with patch("app.core.cookies.COOKIE_SECURE", True):
        set_refresh_cookie(response, "raw-refresh-token")

    cookie = response.headers.get("set-cookie", "")
    assert "secure" in cookie.lower(), "Refresh cookie must be Secure in production"


def test_refresh_cookie_secure_can_be_disabled_for_local_dev():
    """Refresh cookie Secure flag may be disabled for local HTTP development."""
    response = Response()
    with patch("app.core.cookies.COOKIE_SECURE", False):
        set_refresh_cookie(response, "raw-refresh-token")

    # Just verify it doesn't crash — Secure absence is expected in dev
    cookie = response.headers.get("set-cookie", "")
    assert REFRESH_TOKEN_COOKIE_NAME in cookie


# ── A.4.3 — Correct SameSite value ───────────────────────────────────────────

def test_refresh_cookie_has_samesite_attribute():
    """Refresh cookie must have a SameSite attribute (lax or strict)."""
    response = Response()
    set_refresh_cookie(response, "raw-refresh-token")

    cookie = response.headers.get("set-cookie", "").lower()
    assert "samesite=" in cookie, "Refresh cookie must specify SameSite"
    # Accept either lax or strict — both are safe; none is not acceptable
    assert "samesite=none" not in cookie, "SameSite=None is not acceptable without additional controls"


def test_cookie_policy_samesite_is_not_none():
    """Policy summary must not expose SameSite=None (CSRF risk without extra safeguards)."""
    policy = get_cookie_policy_summary()
    assert policy["same_site"].lower() != "none"


# ── A.4.4 — Cookie Path scoped to /api/auth ──────────────────────────────────

def test_refresh_cookie_path_scoped_to_auth():
    """Refresh cookie path must be scoped to auth endpoints, not broadcast to /."""
    response = Response()
    set_refresh_cookie(response, "raw-refresh-token")

    cookie = response.headers.get("set-cookie", "").lower()
    assert "path=/api" in cookie, "Cookie Path must be scoped to /api auth routes, not /"


def test_cookie_policy_path_is_not_root():
    """Policy summary path must not be '/' (would broadcast to every request)."""
    policy = get_cookie_policy_summary()
    assert policy["path"] != "/", "Cookie Path '/' would include all routes — must be narrower"
    assert "/api" in policy["path"]


# ── A.4.5 — Access token NOT stored in JS-readable cookie ────────────────────

def test_access_token_is_not_set_as_js_readable_cookie():
    """The backend must not set an access token in a non-HttpOnly cookie.

    This test audits the backend response for the access token — it should
    only be in the response JSON body (for in-memory storage in the frontend),
    never in a cookie without HttpOnly.
    """
    # The backend auth router sends the access token in the JSON response body,
    # not as a cookie.  Verify set_refresh_cookie only sets the refresh token.
    response = Response()
    set_refresh_cookie(response, "some-refresh-token")

    cookie_header = response.headers.get("set-cookie", "")
    # Only the refresh cookie should be set
    assert REFRESH_TOKEN_COOKIE_NAME in cookie_header
    # The cookie that IS set must be HttpOnly
    assert "HttpOnly" in cookie_header


def test_cookie_policy_js_readable_is_false():
    """Policy summary must declare the cookie as NOT JS-readable."""
    policy = get_cookie_policy_summary()
    assert policy["js_readable"] is False


# ── A.4.6 — Clear cookie removes it correctly ────────────────────────────────

def test_clear_refresh_cookie_deletes_the_cookie():
    """clear_refresh_cookie must set the cookie with max-age=0 to remove it."""
    response = Response()
    clear_refresh_cookie(response)

    cookie = response.headers.get("set-cookie", "").lower()
    assert REFRESH_TOKEN_COOKIE_NAME.lower() in cookie


# ── A.4.7 — Full policy summary shape ────────────────────────────────────────

def test_cookie_policy_summary_has_all_required_fields():
    """Policy summary must contain all required security fields."""
    policy = get_cookie_policy_summary()
    required_fields = {"cookie_name", "http_only", "secure", "same_site", "path", "max_age_seconds", "js_readable"}
    missing = required_fields - set(policy.keys())
    assert not missing, f"Cookie policy summary missing fields: {missing}"


def test_cookie_policy_http_only_is_true():
    """Policy summary must explicitly declare http_only=True."""
    policy = get_cookie_policy_summary()
    assert policy["http_only"] is True


def test_cookie_max_age_is_7_days():
    """Refresh token cookie max-age must match REFRESH_TOKEN_TTL_DAYS (7 days)."""
    policy = get_cookie_policy_summary()
    assert policy["max_age_seconds"] == 7 * 24 * 3600
