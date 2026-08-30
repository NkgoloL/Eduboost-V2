"""Comprehensive unit tests for ContentStagingReadVerificationService models and reports."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.content_staging_read_verification import (
    StagingReadVerificationReport,
    ScopeStagingReadReport,
    ContentStagingReadVerificationService,
)


class TestStagingReadVerificationModels:
    def test_staging_read_verification_report(self):
        srid = uuid.uuid4()
        report = StagingReadVerificationReport(
            seed_run_id=srid,
            passed=True,
            verified_count=40,
            errors=[],
        )
        assert report.seed_run_id == srid
        assert report.passed is True
        assert report.verified_count == 40
        assert len(report.errors) == 0

    def test_scope_staging_read_report(self):
        report = ScopeStagingReadReport(
            scope_id="grade4_mathematics_en",
            passed=True,
            staged_artifacts_count=48,
            errors=[],
        )
        assert report.scope_id == "grade4_mathematics_en"
        assert report.passed is True
        assert report.staged_artifacts_count == 48

    @pytest.mark.asyncio
    async def test_verify_seed_run_empty(self):
        mock_session = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_res

        service = ContentStagingReadVerificationService()
        srid = uuid.uuid4()
        report = await service.verify_seed_run(mock_session, srid)
        assert report.seed_run_id == srid
        assert report.passed is True
        assert report.verified_count == 0
