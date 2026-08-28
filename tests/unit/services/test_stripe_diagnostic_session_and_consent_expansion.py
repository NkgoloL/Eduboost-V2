"""Comprehensive unit tests for Stripe service, DiagnosticSessionRepository, and asyncpg-style ConsentService."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.core.stripe_client import StripeService
from app.repositories.diagnostic_session_repository import DiagnosticSessionRepository
from app.services.consent_service import ConsentService


class TestStripeService:
    def test_stripe_service_init(self):
        mock_db = AsyncMock()
        service = StripeService(db=mock_db)
        assert service._db == mock_db
        assert service._guardian_repo is not None
        assert service._event_repo is not None


class TestDiagnosticSessionRepository:
    def test_repo_init(self):
        mock_db = AsyncMock()
        repo = DiagnosticSessionRepository(db=mock_db)
        assert repo.db == mock_db

    @pytest.mark.asyncio
    async def test_create_session(self):
        mock_db = AsyncMock()
        repo = DiagnosticSessionRepository(db=mock_db)
        lid = uuid.uuid4()

        session = await repo.create_session(learner_id=lid, theta=0.5, se=0.8, caps_ref="4.M.1.1")
        assert session.learner_id == str(lid)
        assert session.theta_before == 0.5
        assert session.se_estimate == 0.8
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_res

        repo = DiagnosticSessionRepository(db=mock_db)
        sid = uuid.uuid4()
        session = await repo.get_session(sid)
        assert session is not None


class TestConsentService:
    def test_consent_service_init(self):
        mock_consent_repo = MagicMock()
        mock_audit_repo = MagicMock()
        service = ConsentService(consent_repo=mock_consent_repo, audit_repo=mock_audit_repo)
        assert service._consent == mock_consent_repo
        assert service._audit == mock_audit_repo
