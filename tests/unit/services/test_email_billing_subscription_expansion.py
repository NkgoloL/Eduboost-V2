from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.email_service import (
    _render,
    _send,
    send_data_export_ready_email,
    send_email_verification,
    send_onboarding_complete_email,
    send_password_reset_email,
)
from app.services.policy_service import (
    LessonPayload,
    PolicyService,
    PolicyValidationError,
    PolicyViolation,
    StudyPlanPayload,
)
from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService


@pytest.mark.asyncio
async def test_email_service_complete():
    # 1. _send with no API key (lines 42-44)
    with patch("os.getenv", return_value=""):
        await _send(to_email="test@example.com", subject="Sub", html_body="<p>Body</p>")

    # 2. _send with API key and 200/202 status (lines 53-62)
    mock_resp_ok = MagicMock(status_code=202, text="Accepted")
    mock_resp_err = MagicMock(status_code=500, text="Internal Error")

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.post.return_value = mock_resp_ok

    with patch("os.getenv", return_value="test-api-key"), \
         patch("httpx.AsyncClient", return_value=mock_client):
        await _send(to_email="ok@example.com", subject="Test", html_body="<p>Hi</p>")
        mock_client.post.assert_awaited_once()

    # 3. _send with API key and error status (line 60)
    mock_client.post.return_value = mock_resp_err
    with patch("os.getenv", return_value="test-api-key"), \
         patch("httpx.AsyncClient", return_value=mock_client):
        await _send(to_email="err@example.com", subject="Test", html_body="<p>Hi</p>")

    # 4. _render helper (line 67)
    with patch("app.services.email_service._env.get_template") as mock_gt:
        mock_gt.return_value.render.return_value = "<html>rendered</html>"
        assert _render("test.html", var="val") == "<html>rendered</html>"

    # 5. high-level senders (lines 70-147)
    with patch("app.services.email_service._render", return_value="<html>Rendered</html>"), \
         patch("app.services.email_service._send", AsyncMock()) as mock_send:

        await send_password_reset_email(
            to_email="u1@example.com",
            learner_name="Learner 1",
            reset_url="https://example.com/reset",
        )
        mock_send.assert_awaited_once()

        mock_send.reset_mock()
        await send_email_verification(
            to_email="u2@example.com",
            learner_name="Learner 2",
            verify_url="https://example.com/verify",
        )
        mock_send.assert_awaited_once()

        mock_send.reset_mock()
        await send_onboarding_complete_email(
            to_email="u3@example.com",
            learner_name="Learner 3",
            dashboard_url="https://example.com/dash",
        )
        mock_send.assert_awaited_once()

        mock_send.reset_mock()
        await send_data_export_ready_email(
            to_email="u4@example.com",
            learner_name="Learner 4",
            export_url="https://example.com/export",
        )
        mock_send.assert_awaited_once()


def test_stripe_service_init():
    mock_db = MagicMock()
    with patch("app.services.stripe_service.require_optional_capability") as mock_cap, \
         patch("app.core.stripe_client.StripeService.__init__", return_value=None):
        svc = StripeService(mock_db)
        mock_cap.assert_called_once_with("billing")
        assert isinstance(svc, StripeService)


@pytest.mark.asyncio
async def test_subscription_service_complete():
    mock_db = MagicMock()
    with patch("app.services.subscription_service.GuardianRepository") as mock_repo_cls, \
         patch("app.services.subscription_service.cache_set", AsyncMock()) as mock_cset, \
         patch("app.services.subscription_service.cache_delete_pattern", AsyncMock()) as mock_cdel:
        mock_repo = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        svc = SubscriptionService(mock_db)

        # 1. activate_premium
        await svc.activate_premium("g-123", "sub-stripe-1")
        mock_repo.update_subscription.assert_awaited_once_with("g-123", "premium", "sub-stripe-1")
        mock_cset.assert_awaited_once_with("user_tier:g-123", "premium", ttl=30 * 24 * 3600)
        mock_cdel.assert_awaited_once_with("ai_quota:g-123:*")

        # 2. downgrade_to_free
        mock_repo.reset_mock()
        mock_cset.reset_mock()
        mock_cdel.reset_mock()

        await svc.downgrade_to_free("g-123")
        mock_repo.update_subscription.assert_awaited_once_with("g-123", "free", None)
        mock_cset.assert_awaited_once_with("user_tier:g-123", "free", ttl=30 * 24 * 3600)
        mock_cdel.assert_awaited_once_with("ai_quota:g-123:*")


def test_policy_service_exports():
    assert PolicyViolation is not None
    assert PolicyService is not None
    assert PolicyValidationError is PolicyViolation
    assert LessonPayload is not None
    assert StudyPlanPayload is not None
