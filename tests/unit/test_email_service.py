"""tests/unit/test_email_service.py
Unit tests for EmailService SendGrid dispatch.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import email_service


@pytest.mark.unit
async def test_send_logs_warning_when_api_key_missing():
    """Verify _send logs warning when SENDGRID_API_KEY not set."""
    with patch.dict("os.environ", {"SENDGRID_API_KEY": ""}):
        with patch("app.services.email_service.logger") as mock_logger:
            await email_service._send(
                to_email="test@example.com",
                subject="Test",
                html_body="<p>Test</p>",
            )
            mock_logger.warning.assert_called_once()
            assert "SENDGRID_API_KEY not set" in mock_logger.warning.call_args[0][0]


@pytest.mark.unit
async def test_send_logs_success_on_200_response():
    """Verify _send logs info on successful SendGrid response."""
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.text = "Accepted"

    with patch.dict("os.environ", {"SENDGRID_API_KEY": "test-key"}):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            with patch("app.services.email_service.logger") as mock_logger:
                await email_service._send(
                    to_email="test@example.com",
                    subject="Test",
                    html_body="<p>Test</p>",
                )
                mock_logger.info.assert_called_once()
                assert "Email sent to %s" in mock_logger.info.call_args[0][0]


@pytest.mark.unit
async def test_send_logs_error_on_non_200_response():
    """Verify _send logs error on SendGrid error response."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    with patch.dict("os.environ", {"SENDGRID_API_KEY": "test-key"}):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            with patch("app.services.email_service.logger") as mock_logger:
                await email_service._send(
                    to_email="test@example.com",
                    subject="Test",
                    html_body="<p>Test</p>",
                )
                mock_logger.error.assert_called_once()
                assert "SendGrid error %s" in mock_logger.error.call_args[0][0]


@pytest.mark.unit
def test_render_renders_template():
    """Verify _render renders Jinja2 template with context."""
    with patch("app.services.email_service._env") as mock_env:
        mock_template = MagicMock()
        mock_template.render.return_value = "<p>Rendered</p>"
        mock_env.get_template.return_value = mock_template

        result = email_service._render("test.html", name="Test")

        assert result == "<p>Rendered</p>"
        mock_env.get_template.assert_called_once_with("test.html")
        mock_template.render.assert_called_once_with(name="Test")


@pytest.mark.unit
async def test_send_password_reset_email_renders_and_sends():
    """Verify send_password_reset_email renders template and sends email."""
    with patch("app.services.email_service._render") as mock_render:
        mock_render.return_value = "<p>Password Reset</p>"
        with patch("app.services.email_service._send") as mock_send:
            await email_service.send_password_reset_email(
                to_email="test@example.com",
                learner_name="John",
                reset_url="https://example.com/reset",
                expires_minutes=30,
            )
            mock_render.assert_called_once_with(
                "password_reset.html",
                learner_name="John",
                reset_url="https://example.com/reset",
                expires_minutes=30,
            )
            mock_send.assert_called_once()
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs["to_email"] == "test@example.com"
            assert "Reset your password" in call_kwargs["subject"]


@pytest.mark.unit
async def test_send_email_verification_renders_and_sends():
    """Verify send_email_verification renders template and sends email."""
    with patch("app.services.email_service._render") as mock_render:
        mock_render.return_value = "<p>Verify Email</p>"
        with patch("app.services.email_service._send") as mock_send:
            await email_service.send_email_verification(
                to_email="test@example.com",
                learner_name="John",
                verify_url="https://example.com/verify",
                expires_hours=24,
            )
            mock_render.assert_called_once_with(
                "email_verify.html",
                learner_name="John",
                verify_url="https://example.com/verify",
                expires_hours=24,
            )
            mock_send.assert_called_once()
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs["to_email"] == "test@example.com"
            assert "Verify your email address" in call_kwargs["subject"]


@pytest.mark.unit
async def test_send_onboarding_complete_email_renders_and_sends():
    """Verify send_onboarding_complete_email renders template and sends email."""
    with patch("app.services.email_service._render") as mock_render:
        mock_render.return_value = "<p>Onboarding Complete</p>"
        with patch("app.services.email_service._send") as mock_send:
            await email_service.send_onboarding_complete_email(
                to_email="test@example.com",
                learner_name="John",
                dashboard_url="https://example.com/dashboard",
            )
            mock_render.assert_called_once_with(
                "onboarding_complete.html",
                learner_name="John",
                dashboard_url="https://example.com/dashboard",
            )
            mock_send.assert_called_once()
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs["to_email"] == "test@example.com"
            assert "You're all set" in call_kwargs["subject"]


@pytest.mark.unit
async def test_send_data_export_ready_email_renders_and_sends():
    """Verify send_data_export_ready_email renders template and sends email."""
    with patch("app.services.email_service._render") as mock_render:
        mock_render.return_value = "<p>Data Export Ready</p>"
        with patch("app.services.email_service._send") as mock_send:
            await email_service.send_data_export_ready_email(
                to_email="test@example.com",
                learner_name="John",
                export_url="https://example.com/export",
            )
            mock_render.assert_called_once_with(
                "data_export.html",
                learner_name="John",
                export_url="https://example.com/export",
            )
            mock_send.assert_called_once()
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs["to_email"] == "test@example.com"
            assert "Your data export is ready" in call_kwargs["subject"]
