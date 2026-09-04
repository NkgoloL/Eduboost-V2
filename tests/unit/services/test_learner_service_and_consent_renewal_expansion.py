"""Comprehensive unit tests for LearnerService and Consent Renewal Reminder gateway."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.learner_service import LearnerService
from app.services.consent_renewal_service import SendGridEmailGateway


class TestLearnerServiceInitialization:
    def test_learner_service_init_default(self):
        mock_db = AsyncMock()
        service = LearnerService(db=mock_db)
    def test_learner_service_init(self):
        mock_db = AsyncMock()
        service = LearnerService(db=mock_db)
        assert service.db == mock_db
        assert service.repository is not None
        mock_repo = MagicMock()
        service.repository = mock_repo
        assert service.repository == mock_repo


class TestSendGridEmailGateway:
    def test_build_html_urgent_vs_upcoming(self):
        # 5 days left -> urgent
        html_urgent = SendGridEmailGateway._build_html(days_left=5, renewal_url="https://eduboost.co.za/renew?id=123")
        assert "urgent" in html_urgent
        assert "5 day(s)" in html_urgent
        assert "https://eduboost.co.za/renew?id=123" in html_urgent

        # 25 days left -> upcoming
        html_upcoming = SendGridEmailGateway._build_html(days_left=25, renewal_url="https://eduboost.co.za/renew?id=456")
        assert "upcoming" in html_upcoming
        assert "25 day(s)" in html_upcoming

    def test_gateway_init(self):
        mock_settings = MagicMock()
        gateway = SendGridEmailGateway(settings=mock_settings)
        assert gateway._settings == mock_settings
        assert gateway._client is None
