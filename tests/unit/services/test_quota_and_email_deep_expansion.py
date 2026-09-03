"""Comprehensive unit tests for QuotaService key generation and EmailService SendGrid dispatch."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.email_service import (
    FROM_NAME,
    SENDGRID_API_URL,
    _send,
    send_data_export_ready_email,
    send_email_verification,
    send_onboarding_complete_email,
    send_password_reset_email,
)
from app.services.quota_service import (
    _CACHE_KEY,
    _QUOTA_KEY,
    QuotaExceededError,
    QuotaService,
    SemanticCacheService,
)


class TestQuotaService:
    def test_quota_and_cache_key_patterns(self):
        assert "quota:{guardian_id}:{date}" == _QUOTA_KEY
        assert "semcache:{hash}" == _CACHE_KEY

    def test_quota_exceeded_error_type(self):
        err = QuotaExceededError("Quota reached")
        assert isinstance(err, RuntimeError)
        assert str(err) == "Quota reached"

    def test_quota_service_key_generation(self):
        service = QuotaService()
        key = service._quota_key("guard-123")
        assert key.startswith("quota:guard-123:")

    @pytest.mark.asyncio
    async def test_check_and_reserve_flows(self):
        mock_redis = AsyncMock()
        service = QuotaService(redis_client=mock_redis)

        # 1. First increment sets expiry
        mock_redis.incrby.return_value = 1000
        await service.check_and_reserve("guard-1", 1000, tier="free")
        mock_redis.expire.assert_called_with(service._quota_key("guard-1"), 86400)

        # 2. Quota exceeded -> rollback and 429
        mock_redis.incrby.return_value = 99999999
        with pytest.raises(HTTPException) as exc_info:
            await service.check_and_reserve("guard-1", 5000, tier="free")
        assert exc_info.value.status_code == 429
        mock_redis.decrby.assert_called_with(service._quota_key("guard-1"), 5000)

    @pytest.mark.asyncio
    async def test_get_usage_and_increment_requests(self):
        mock_redis = AsyncMock()
        service = QuotaService(redis_client=mock_redis)

        mock_redis.get.side_effect = [b"1200", b"5"]
        tokens, reqs = await service.get_usage("guard-1")
        assert tokens == 1200
        assert reqs == 5

        # increment requests
        await service.increment_requests("guard-1")
        mock_redis.incr.assert_called()


class TestSemanticCacheService:
    def test_build_cache_key(self):
        key1 = SemanticCacheService.build_cache_key("Math", "Addition", "4", "en", "visual")
        key2 = SemanticCacheService.build_cache_key("Math", "Addition", "4", "en", None)
        assert key1.startswith("semcache:")
        assert key2.startswith("semcache:")
        assert key1 != key2

    @pytest.mark.asyncio
    async def test_get_and_set_cache(self):
        mock_redis = AsyncMock()
        cache = SemanticCacheService(redis_client=mock_redis)

        # disabled cache
        with patch("app.services.quota_service.settings") as mock_settings:
            mock_settings.semantic_cache_enabled = False
            assert await cache.get("key1") is None
            await cache.set("key1", "{}")
            mock_redis.setex.assert_not_called()

        # enabled cache miss and hit
        with patch("app.services.quota_service.settings") as mock_settings:
            mock_settings.semantic_cache_enabled = True
            mock_settings.redis_cache_ttl_seconds = 3600
            mock_redis.get.return_value = b'{"lesson": 1}'
            res_bytes = await cache.get("key1")
            assert res_bytes == '{"lesson": 1}'

            mock_redis.get.return_value = '{"lesson": 2}'
            res_str = await cache.get("key2")
            assert res_str == '{"lesson": 2}'

            mock_redis.get.return_value = None
            assert await cache.get("key3") is None

            await cache.set("key1", '{"lesson": 1}')
            mock_redis.setex.assert_called()


class TestEmailService:
    def test_sendgrid_constants(self):
        assert SENDGRID_API_URL == "https://api.sendgrid.com/v3/mail/send"
        assert FROM_NAME == "EduBoost SA"

    @pytest.mark.asyncio
    async def test_send_without_api_key_skips_cleanly(self):
        with patch.dict(os.environ, {"SENDGRID_API_KEY": ""}, clear=False):
            await _send(
                to_email="test@example.com",
                subject="Test Subject",
                html_body="<p>Test body</p>",
            )

    @pytest.mark.asyncio
    async def test_send_with_api_key_mock_http(self):
        mock_resp_success = MagicMock(status_code=202, text="Accepted")
        mock_resp_error = MagicMock(status_code=500, text="Internal Server Error")

        with patch.dict(os.environ, {"SENDGRID_API_KEY": "SG.mock_key"}, clear=False):
            with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
                # 1. Success 202
                mock_post.return_value = mock_resp_success
                await _send(to_email="test@example.com", subject="Subj", html_body="<p>Hi</p>")

                # 2. Error 500
                mock_post.return_value = mock_resp_error
                await _send(to_email="test@example.com", subject="Subj", html_body="<p>Hi</p>")

    @pytest.mark.asyncio
    async def test_public_email_dispatchers(self):
        with patch("app.services.email_service._send", new_callable=AsyncMock) as mock_send:
            with patch("app.services.email_service._render", return_value="<html>body</html>"):
                await send_password_reset_email(to_email="u@example.com", learner_name="Learner", reset_url="https://reset")
                await send_email_verification(to_email="u@example.com", learner_name="Learner", verify_url="https://verify")
                await send_onboarding_complete_email(to_email="u@example.com", learner_name="Learner", dashboard_url="https://dash")
                await send_data_export_ready_email(to_email="u@example.com", learner_name="Learner", export_url="https://export")
                assert mock_send.call_count == 4
