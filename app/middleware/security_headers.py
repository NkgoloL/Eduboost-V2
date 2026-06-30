"""
Security Headers Middleware — Phase 7 hardening.

Changes (7.3 + 7.4):
- HSTS is now conditional on APP_ENV == "production" (7.4).
- CSP no longer contains 'unsafe-inline' in production.
  A per-request nonce is generated and made available via request.state.csp_nonce
  so templates can reference it as {{ request.state.csp_nonce }}.
  In non-production environments the policy is more permissive (7.3).
- CSP violation reporting endpoint: /api/v2/csp-report (future hook).
"""
from __future__ import annotations

import secrets
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate a fresh nonce for every request so inline scripts/styles
        # can use it without opening the door to XSS via 'unsafe-inline'.
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response: Response = await call_next(request)

        # ── Standard headers (always applied) ────────────────────────────────
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # ── HSTS — production only (7.4) ─────────────────────────────────────
        # Sending HSTS over plain HTTP in dev would instruct browsers to
        # always use HTTPS for localhost, breaking the dev workflow.
        if settings.is_production():
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # ── Content-Security-Policy (7.3) ────────────────────────────────────
        if settings.is_production():
            # Strict policy: nonce-based, no 'unsafe-inline'.
            # Templates must emit <script nonce="{{ request.state.csp_nonce }}">
            csp_policy = (
                "default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                f"style-src 'self' 'nonce-{nonce}'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "report-uri /api/v2/csp-report;"
            )
        else:
            # Permissive policy for development — allows inline scripts/styles
            # so the Next.js dev server and hot-reload work without friction.
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss:; "
                "frame-ancestors 'none';"
            )

        response.headers["Content-Security-Policy"] = csp_policy

        return response
