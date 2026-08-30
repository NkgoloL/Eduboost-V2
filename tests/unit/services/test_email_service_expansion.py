"""Batch 204: Unit tests for email_service async email dispatch helpers."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


# ─────────────────────────────────────────────
# _send internal dispatcher
# ─────────────────────────────────────────────


class TestSendDispatcher:
    @pytest.mark.asyncio
    async def test_no_api_key_skips_send(self, caplog):
        """When SENDGRID_API_KEY is not set, the email should be skipped."""
        import logging
        from app.services import email_service
        with patch.dict("os.environ", {"SENDGRID_API_KEY": ""}, clear=False):
            with caplog.at_level(logging.WARNING, logger="app.services.email_service"):
                await email_service._send(
                    to_email="user@example.com",
                    subject="Test Subject",
                    html_body="<h1>Hello</h1>",
                )
        assert any("skipped" in r.message or "SENDGRID_API_KEY" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_successful_send_202(self):
        """When SendGrid returns 202, no error is raised."""
        from app.services import email_service

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.text = "Accepted"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.dict("os.environ", {"SENDGRID_API_KEY": "test-key-123"}):
            with patch("httpx.AsyncClient", return_value=mock_client):
                # Should not raise
                await email_service._send(
                    to_email="user@example.com",
                    subject="Test",
                    html_body="<p>Test</p>",
                )

    @pytest.mark.asyncio
    async def test_failed_send_logs_error(self, caplog):
        """When SendGrid returns 400, the error is logged."""
        import logging
        from app.services import email_service

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.dict("os.environ", {"SENDGRID_API_KEY": "test-key-123"}):
            with patch("httpx.AsyncClient", return_value=mock_client):
                with caplog.at_level(logging.ERROR, logger="app.services.email_service"):
                    await email_service._send(
                        to_email="user@example.com",
                        subject="Test",
                        html_body="<p>Test</p>",
                    )
        assert any("SendGrid error" in r.message or "400" in r.message for r in caplog.records)


# ─────────────────────────────────────────────
# Public email helpers — mocking _send and _render
# ─────────────────────────────────────────────


class TestSendPasswordResetEmail:
    @pytest.mark.asyncio
    async def test_calls_send_with_correct_subject(self):
        from app.services import email_service

        sent_calls = []

        async def mock_send(**kwargs):
            sent_calls.append(kwargs)

        with patch.object(email_service, "_send", side_effect=mock_send):
            with patch.object(email_service, "_render", return_value="<html>Reset</html>"):
                await email_service.send_password_reset_email(
                    to_email="guardian@example.com",
                    learner_name="Thabo",
                    reset_url="https://eduboost.co.za/reset?token=abc",
                )

        assert len(sent_calls) == 1
        assert sent_calls[0]["to_email"] == "guardian@example.com"
        assert "Reset" in sent_calls[0]["subject"] or "password" in sent_calls[0]["subject"].lower()

    @pytest.mark.asyncio
    async def test_render_called_with_correct_template(self):
        from app.services import email_service

        render_calls = []

        def mock_render(template_name, **kwargs):
            render_calls.append((template_name, kwargs))
            return "<html>Reset</html>"

        async def mock_send(**kwargs):
            pass

        with patch.object(email_service, "_send", side_effect=mock_send):
            with patch.object(email_service, "_render", side_effect=mock_render):
                await email_service.send_password_reset_email(
                    to_email="user@example.com",
                    learner_name="Nomsa",
                    reset_url="https://reset.url",
                    expires_minutes=60,
                )

        assert render_calls[0][0] == "password_reset.html"
        assert render_calls[0][1]["learner_name"] == "Nomsa"
        assert render_calls[0][1]["expires_minutes"] == 60


class TestSendEmailVerification:
    @pytest.mark.asyncio
    async def test_calls_send_with_verification_template(self):
        from app.services import email_service

        render_calls = []

        def mock_render(template_name, **kwargs):
            render_calls.append((template_name, kwargs))
            return "<html>Verify</html>"

        async def mock_send(**kwargs):
            pass

        with patch.object(email_service, "_send", side_effect=mock_send):
            with patch.object(email_service, "_render", side_effect=mock_render):
                await email_service.send_email_verification(
                    to_email="learner@example.com",
                    learner_name="Sipho",
                    verify_url="https://verify.url",
                    expires_hours=48,
                )

        assert render_calls[0][0] == "email_verify.html"
        assert render_calls[0][1]["expires_hours"] == 48


class TestSendOnboardingCompleteEmail:
    @pytest.mark.asyncio
    async def test_calls_onboarding_template(self):
        from app.services import email_service

        render_calls = []

        def mock_render(template_name, **kwargs):
            render_calls.append((template_name, kwargs))
            return "<html>Welcome</html>"

        async def mock_send(**kwargs):
            pass

        with patch.object(email_service, "_send", side_effect=mock_send):
            with patch.object(email_service, "_render", side_effect=mock_render):
                await email_service.send_onboarding_complete_email(
                    to_email="parent@example.com",
                    learner_name="Zanele",
                    dashboard_url="https://app.eduboost.co.za/dashboard",
                )

        assert render_calls[0][0] == "onboarding_complete.html"
        assert render_calls[0][1]["learner_name"] == "Zanele"


class TestSendDataExportReadyEmail:
    @pytest.mark.asyncio
    async def test_calls_data_export_template(self):
        from app.services import email_service

        render_calls = []

        def mock_render(template_name, **kwargs):
            render_calls.append((template_name, kwargs))
            return "<html>Export</html>"

        async def mock_send(**kwargs):
            pass

        with patch.object(email_service, "_send", side_effect=mock_send):
            with patch.object(email_service, "_render", side_effect=mock_render):
                await email_service.send_data_export_ready_email(
                    to_email="guardian@example.com",
                    learner_name="Mandla",
                    export_url="https://exports.eduboost.co.za/dl/abc",
                )

        assert render_calls[0][0] == "data_export.html"
        assert render_calls[0][1]["export_url"] == "https://exports.eduboost.co.za/dl/abc"


# ─────────────────────────────────────────────
# Module-level constants
# ─────────────────────────────────────────────


class TestEmailServiceConstants:
    def test_sendgrid_api_url(self):
        from app.services.email_service import SENDGRID_API_URL
        assert "sendgrid.com" in SENDGRID_API_URL
        assert "https" in SENDGRID_API_URL

    def test_from_address_is_string(self):
        from app.services.email_service import FROM_ADDRESS, FROM_NAME
        assert isinstance(FROM_ADDRESS, str)
        assert isinstance(FROM_NAME, str)
        assert "@" in FROM_ADDRESS or FROM_ADDRESS  # either a real address or env override
