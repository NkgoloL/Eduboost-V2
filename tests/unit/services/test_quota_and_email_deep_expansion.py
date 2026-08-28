"""Comprehensive unit tests for QuotaService key generation and EmailService SendGrid dispatch."""
from __future__ import annotations

import os
from unittest.mock import patch
import pytest

from app.services.quota_service import (
    _QUOTA_KEY,
    _CACHE_KEY,
    QuotaExceededError,
    QuotaService,
)
from app.services.email_service import (
    SENDGRID_API_URL,
    FROM_NAME,
    _send,
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


class TestEmailService:
    def test_sendgrid_constants(self):
        assert SENDGRID_API_URL == "https://api.sendgrid.com/v3/mail/send"
        assert FROM_NAME == "EduBoost SA"

    @pytest.mark.asyncio
    async def test_send_without_api_key_skips_cleanly(self):
        with patch.dict(os.environ, {"SENDGRID_API_KEY": ""}, clear=False):
            # Should skip without raising any exceptions
            await _send(
                to_email="test@example.com",
                subject="Test Subject",
                html_body="<p>Test body</p>",
            )
