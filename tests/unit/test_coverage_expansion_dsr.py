"""
Unit tests for app.services.data_subject_rights_service module.
Covers DSR data export, erasure, correction, and restriction handling with mocked Pool and AuditRepository.
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.domain.data_subject_rights import (
    RequestStatus,
)
from app.services.data_subject_rights_service import DataSubjectRightsService


@pytest.fixture
def mock_pool():
    pool = AsyncMock()
    pool.execute = AsyncMock()
    pool.fetchrow = AsyncMock()
    pool.fetch = AsyncMock(return_value=[])
    return pool


@pytest.fixture
def mock_audit():
    audit = AsyncMock()
    audit.record = AsyncMock()
    return audit


@pytest.fixture
def dsr_service(mock_pool, mock_audit):
    return DataSubjectRightsService(pool=mock_pool, audit_repo=mock_audit)


class TestDataSubjectRightsService:
    @pytest.mark.asyncio
    async def test_create_export_request(self, dsr_service, mock_pool, mock_audit):
        learner_id = uuid.uuid4()
        requested_by = uuid.uuid4()

        req = await dsr_service.create_export_request(learner_id, requested_by, fmt="json")
        assert req.learner_id == learner_id
        assert req.requested_by == requested_by
        assert req.format == "json"
        assert req.status == RequestStatus.PENDING
        mock_pool.execute.assert_called_once()
        mock_audit.record.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_export_status_none(self, dsr_service, mock_pool):
        mock_pool.fetchrow.return_value = None
        req = await dsr_service.get_export_status(uuid.uuid4())
        assert req is None

    @pytest.mark.asyncio
    async def test_create_erasure_request(self, dsr_service, mock_pool, mock_audit):
        learner_id = uuid.uuid4()
        requested_by = uuid.uuid4()

        req = await dsr_service.create_erasure_request(learner_id, requested_by)
        assert req.learner_id == learner_id
        assert req.status == RequestStatus.PENDING
        mock_pool.execute.assert_called_once()
        mock_audit.record.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_correction_request(self, dsr_service, mock_pool, mock_audit):
        learner_id = uuid.uuid4()
        requested_by = uuid.uuid4()
        field_name = "first_name"
        new_value = "Jane"

        req = await dsr_service.create_correction_request(learner_id, requested_by, field_name, new_value)
        assert req.learner_id == learner_id
        assert req.field_name == field_name
        assert req.new_value == new_value
        mock_pool.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_restriction_request(self, dsr_service, mock_pool, mock_audit):
        learner_id = uuid.uuid4()
        requested_by = uuid.uuid4()
        reason = "Disputed processing"

        req = await dsr_service.create_restriction_request(learner_id, requested_by, reason)
        assert req.learner_id == learner_id
        assert req.reason == reason
        mock_pool.execute.assert_called_once()
