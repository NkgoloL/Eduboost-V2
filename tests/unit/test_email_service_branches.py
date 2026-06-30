"""tests/unit/test_email_service_branches.py
Additional branch-focused tests for email_service without network I/O.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from jinja2 import TemplateNotFound

from app.services import email_service


@pytest.mark.unit
def test_render_missing_template_raises():
    with patch("app.services.email_service._env") as mock_env:
        mock_env.get_template.side_effect = TemplateNotFound("missing.html")
        with pytest.raises(TemplateNotFound):
            email_service._render("missing.html")


@pytest.mark.unit
async def test_password_reset_propagates_render_error_and_skips_send():
    with patch("app.services.email_service._render") as mock_render:
        mock_render.side_effect = TemplateNotFound("password_reset.html")
        with patch("app.services.email_service._send", new_callable=AsyncMock) as mock_send:
            with pytest.raises(TemplateNotFound):
                await email_service.send_password_reset_email(
                    to_email="user@example.com",
                    learner_name="Learner",
                    reset_url="https://example/reset",
                )
            mock_send.assert_not_called()


@pytest.mark.unit
async def test_send_raises_on_httpx_exception(monkeypatch):
    # Emulate enabled sending
    monkeypatch.setenv("SENDGRID_API_KEY", "key")
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(side_effect=httpx.HTTPError("boom"))
        with pytest.raises(httpx.HTTPError):
            await email_service._send(to_email="u@example.com", subject="S", html_body="<p>x</p>")


@pytest.mark.unit
async def test_send_payload_contains_invalid_recipient(monkeypatch):
    # No format validation in service; ensure payload carries through
    monkeypatch.setenv("SENDGRID_API_KEY", "key")
    with patch("httpx.AsyncClient") as mock_client:
        mock_resp = MagicMock()
        mock_resp.status_code = 202
        mock_resp.text = "Accepted"
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)

        invalid_email = "not-an-email"
        await email_service._send(to_email=invalid_email, subject="S", html_body="<p>x</p>")

        post_call = mock_client.return_value.__aenter__.return_value.post
        sent_json = post_call.call_args.kwargs["json"]
        assert sent_json["personalizations"][0]["to"][0]["email"] == invalid_email
