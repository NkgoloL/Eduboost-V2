"""
email_service.py — EduBoost SA V2
Centralised async email dispatch via SendGrid.
Renders Jinja2 HTML templates stored in app/templates/email/.

Place at:
    app/services/email_service.py

Required env vars:
    SENDGRID_API_KEY   — SendGrid API key (v3)
    SENDGRID_FROM_EMAIL — sender address (defaults to noreply@eduboost.co.za)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Template directory — adjust path if your layout differs
_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "email"
_env = Environment(
    loader      = FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape  = select_autoescape(["html"]),
)

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
FROM_ADDRESS     = os.getenv("SENDGRID_FROM_EMAIL", "noreply@eduboost.co.za")
FROM_NAME        = "EduBoost SA"


# ── Internal dispatcher ───────────────────────────────────────────────────────

async def _send(*, to_email: str, subject: str, html_body: str) -> None:
    """Fire-and-forget async POST to SendGrid. Logs but does NOT raise on failure."""
    api_key = os.getenv("SENDGRID_API_KEY", "")
    if not api_key:
        logger.warning("SENDGRID_API_KEY not set — email to %s skipped", to_email)
        return

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from":    {"email": FROM_ADDRESS, "name": FROM_NAME},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_body}],
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            SENDGRID_API_URL,
            json    = payload,
            headers = {"Authorization": f"Bearer {api_key}"},
        )
        if resp.status_code not in (200, 202):
            logger.error("SendGrid error %s: %s", resp.status_code, resp.text)
        else:
            logger.info("Email sent to %s [%s]", to_email, subject)


def _render(template_name: str, **ctx) -> str:
    """Render a Jinja2 template from the email template directory."""
    return _env.get_template(template_name).render(**ctx)


# ── Public helpers ────────────────────────────────────────────────────────────

async def send_password_reset_email(
    *,
    to_email:        str,
    learner_name:    str,
    reset_url:       str,
    expires_minutes: int = 30,
) -> None:
    html = _render(
        "password_reset.html",
        learner_name    = learner_name,
        reset_url       = reset_url,
        expires_minutes = expires_minutes,
    )
    await _send(
        to_email  = to_email,
        subject   = "EduBoost SA — Reset your password",
        html_body = html,
    )


async def send_email_verification(
    *,
    to_email:      str,
    learner_name:  str,
    verify_url:    str,
    expires_hours: int = 24,
) -> None:
    html = _render(
        "email_verify.html",
        learner_name  = learner_name,
        verify_url    = verify_url,
        expires_hours = expires_hours,
    )
    await _send(
        to_email  = to_email,
        subject   = "EduBoost SA — Verify your email address",
        html_body = html,
    )


async def send_onboarding_complete_email(
    *,
    to_email:      str,
    learner_name:  str,
    dashboard_url: str,
) -> None:
    html = _render(
        "onboarding_complete.html",
        learner_name  = learner_name,
        dashboard_url = dashboard_url,
    )
    await _send(
        to_email  = to_email,
        subject   = "EduBoost SA — You're all set! 🦁",
        html_body = html,
    )


async def send_data_export_ready_email(
    *,
    to_email:     str,
    learner_name: str,
    export_url:   str,
) -> None:
    """Called by the background job when a POPIA data export is ready."""
    html = _render(
        "data_export.html",
        learner_name = learner_name,
        export_url   = export_url,
    )
    await _send(
        to_email  = to_email,
        subject   = "EduBoost SA — Your data export is ready",
        html_body = html,
    )
