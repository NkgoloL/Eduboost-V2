"""
Integration tests for SecurityHeadersMiddleware — Phase 7 hardening.

Coverage:
- Standard headers always present (7.3, 7.4)
- HSTS is conditional on APP_ENV == "production" (7.4)
- CSP contains 'unsafe-inline' in dev, NOT in production (7.3)
- CSP contains a nonce in production (7.3)
- Nonce is unique per request (7.3)
- Permissions-Policy header present (7.3)
"""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch

pytestmark = pytest.mark.integration


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_client(app):
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ── Standard headers (always present regardless of APP_ENV) ──────────────────

@pytest.mark.asyncio
async def test_standard_headers_always_present():
    """X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
    must be present in both dev and production modes."""
    from app.api_v2 import app

    async with _make_client(app) as client:
        response = await client.get("/health")

    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("Permissions-Policy") == "geolocation=(), microphone=(), camera=()"


# ── HSTS — conditional on APP_ENV (7.4) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_hsts_absent_in_development():
    """HSTS must NOT be present when APP_ENV != 'production'.
    Phase 7.4 — fixes the original test that assumed HSTS was always set.
    """
    from app.api_v2 import app

    # Default APP_ENV in test/dev mode is 'development' or 'test'
    async with _make_client(app) as client:
        response = await client.get("/health")

    assert "strict-transport-security" not in response.headers, (
        "HSTS must not be sent over non-production HTTP — it would instruct "
        "browsers to always use HTTPS for localhost, breaking dev workflows."
    )


@pytest.mark.asyncio
async def test_hsts_present_in_production():
    """HSTS must be present when APP_ENV == 'production'."""
    from app.api_v2 import app
    from app.core.config import settings

    with patch.object(settings.__class__, "is_production", return_value=True):
        async with _make_client(app) as client:
            response = await client.get("/health")

    hsts = response.headers.get("strict-transport-security", "")
    assert "max-age=31536000" in hsts, "HSTS max-age must be set in production"
    assert "includeSubDomains" in hsts, "HSTS must include subdomains in production"


# ── CSP — nonce-based in production, permissive in dev (7.3) ─────────────────

@pytest.mark.asyncio
async def test_csp_dev_is_permissive():
    """Development CSP must allow 'unsafe-inline' so the Next.js dev server works."""
    from app.api_v2 import app

    async with _make_client(app) as client:
        response = await client.get("/health")

    csp = response.headers.get("content-security-policy", "")
    assert csp, "Content-Security-Policy header must be present"
    assert "unsafe-inline" in csp, (
        "Development CSP must contain 'unsafe-inline' to allow Next.js HMR"
    )


@pytest.mark.asyncio
async def test_csp_production_has_no_unsafe_inline():
    """Production CSP must NOT contain 'unsafe-inline' — nonce-based only (7.3)."""
    from app.api_v2 import app
    from app.core.config import settings

    with patch.object(settings.__class__, "is_production", return_value=True):
        async with _make_client(app) as client:
            response = await client.get("/health")

    csp = response.headers.get("content-security-policy", "")
    assert csp, "Content-Security-Policy header must be present in production"
    assert "unsafe-inline" not in csp, (
        "Production CSP must not contain 'unsafe-inline' — use nonce-based CSP instead"
    )


@pytest.mark.asyncio
async def test_csp_production_contains_nonce():
    """Production CSP must contain a per-request nonce for script-src and style-src."""
    from app.api_v2 import app
    from app.core.config import settings

    with patch.object(settings.__class__, "is_production", return_value=True):
        async with _make_client(app) as client:
            response = await client.get("/health")

    csp = response.headers.get("content-security-policy", "")
    assert "nonce-" in csp, "Production CSP must contain 'nonce-<value>' for script-src/style-src"


@pytest.mark.asyncio
async def test_csp_nonce_unique_per_request():
    """Each request must receive a unique nonce (replay-attack prevention)."""
    from app.api_v2 import app
    from app.core.config import settings

    with patch.object(settings.__class__, "is_production", return_value=True):
        async with _make_client(app) as client:
            r1 = await client.get("/health")
            r2 = await client.get("/health")

    def _extract_nonce(csp: str) -> str:
        for part in csp.split(";"):
            part = part.strip()
            if "nonce-" in part:
                # e.g. "script-src 'self' 'nonce-abc123'"
                for token in part.split():
                    if token.startswith("'nonce-"):
                        return token
        return ""

    nonce1 = _extract_nonce(r1.headers.get("content-security-policy", ""))
    nonce2 = _extract_nonce(r2.headers.get("content-security-policy", ""))

    assert nonce1, "First response must contain a nonce"
    assert nonce2, "Second response must contain a nonce"
    assert nonce1 != nonce2, "Each request must get a unique nonce"


@pytest.mark.asyncio
async def test_csp_production_has_report_uri():
    """Production CSP must include a report-uri for violation monitoring."""
    from app.api_v2 import app
    from app.core.config import settings

    with patch.object(settings.__class__, "is_production", return_value=True):
        async with _make_client(app) as client:
            response = await client.get("/health")

    csp = response.headers.get("content-security-policy", "")
    assert "report-uri" in csp, "Production CSP should include report-uri for violation monitoring"


# ── CSP framing defence (always) ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_csp_frame_ancestors_none():
    """Both dev and production CSP must prevent framing ('frame-ancestors none')."""
    from app.api_v2 import app

    async with _make_client(app) as client:
        response = await client.get("/health")

    csp = response.headers.get("content-security-policy", "")
    assert "frame-ancestors 'none'" in csp, (
        "CSP must prevent embedding in iframes in all environments"
    )
