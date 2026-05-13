"""
tests/integration/test_popia_data_subject_rights.py
§4.3 – Integration tests for export, erasure, correction, restriction workflows.
Uses an in-memory fake pool for speed; replace with real asyncpg pool for full e2e.
"""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.data_subject_rights import (
    DataExportRequest,
    ErasureRequest,
    CorrectionRequest,
    RestrictionRequest,
    RequestStatus,
)
from app.services.data_subject_rights_service import DataSubjectRightsService


# ---------------------------------------------------------------------------
# Minimal fake DB pool
# ---------------------------------------------------------------------------

class _FakePool:
    """In-memory store that mimics asyncpg pool enough for unit-level integration."""

    def __init__(self):
        self._tables: dict[str, dict[uuid.UUID, dict]] = defaultdict(dict)

    async def execute(self, sql: str, *args):
        # Parse INSERT / UPDATE crudely for test purposes
        pass

    async def fetchrow(self, sql: str, *args):
        return None

    async def fetch(self, sql: str, *args):
        return []

    def acquire(self):
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=self)
        ctx.__aexit__ = AsyncMock(return_value=False)
        return ctx

    def transaction(self):
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=None)
        ctx.__aexit__ = AsyncMock(return_value=False)
        return ctx


# ---------------------------------------------------------------------------
# §4.3 Export workflow
# ---------------------------------------------------------------------------

class TestExportWorkflow:
    def _svc(self) -> DataSubjectRightsService:
        pool = _FakePool()
        audit = AsyncMock()
        return DataSubjectRightsService(pool, audit)

    @pytest.mark.asyncio
    async def test_create_export_request_returns_pending(self):
        svc = self._svc()
        learner_id = uuid.uuid4()
        guardian_id = uuid.uuid4()
        req = await svc.create_export_request(learner_id, guardian_id, fmt="json")
        assert req.status == RequestStatus.PENDING
        assert req.learner_id == learner_id
        assert req.format == "json"

    @pytest.mark.asyncio
    async def test_create_csv_export_request(self):
        svc = self._svc()
        req = await svc.create_export_request(uuid.uuid4(), uuid.uuid4(), fmt="csv")
        assert req.format == "csv"

    @pytest.mark.asyncio
    async def test_export_request_has_sla_deadline(self):
        svc = self._svc()
        req = await svc.create_export_request(uuid.uuid4(), uuid.uuid4())
        assert req.sla_deadline > datetime.now(timezone.utc)

    @pytest.mark.asyncio
    async def test_export_audit_event_fired(self):
        pool = _FakePool()
        audit = AsyncMock()
        svc = DataSubjectRightsService(pool, audit)
        await svc.create_export_request(uuid.uuid4(), uuid.uuid4())
        audit.record.assert_called_once()


# ---------------------------------------------------------------------------
# §4.3 Erasure workflow
# ---------------------------------------------------------------------------

class TestErasureWorkflow:
    def _svc(self) -> DataSubjectRightsService:
        return DataSubjectRightsService(_FakePool(), AsyncMock())

    @pytest.mark.asyncio
    async def test_create_erasure_request_pending(self):
        svc = self._svc()
        req = await svc.create_erasure_request(uuid.uuid4(), uuid.uuid4())
        assert req.status == RequestStatus.PENDING
        assert req.legal_hold is False

    @pytest.mark.asyncio
    async def test_erasure_cannot_execute_in_pending_state(self):
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            status=RequestStatus.PENDING,
        )
        assert req.can_execute() is False

    @pytest.mark.asyncio
    async def test_erasure_cannot_execute_with_legal_hold(self):
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            status=RequestStatus.IN_PROGRESS,
            legal_hold=True,
        )
        assert req.can_execute() is False

    @pytest.mark.asyncio
    async def test_erasure_can_execute_when_approved(self):
        req = ErasureRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            status=RequestStatus.IN_PROGRESS,
            legal_hold=False,
        )
        assert req.can_execute() is True


# ---------------------------------------------------------------------------
# §4.3 Correction workflow
# ---------------------------------------------------------------------------

class TestCorrectionWorkflow:
    @pytest.mark.asyncio
    async def test_create_correction_request(self):
        pool = _FakePool()
        audit = AsyncMock()
        svc = DataSubjectRightsService(pool, audit)
        req = await svc.create_correction_request(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            field_name="first_name",
            new_value="Amara",
            old_value="Amira",
        )
        assert req.field_name == "first_name"
        assert req.new_value == "Amara"
        assert req.status == RequestStatus.PENDING


# ---------------------------------------------------------------------------
# §4.3 Processing Restriction workflow
# ---------------------------------------------------------------------------

class TestRestrictionWorkflow:
    @pytest.mark.asyncio
    async def test_create_restriction_request(self):
        pool = _FakePool()
        audit = AsyncMock()
        svc = DataSubjectRightsService(pool, audit)
        req = await svc.create_restriction_request(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            reason="contesting accuracy of data",
        )
        assert req.reason == "contesting accuracy of data"
        assert req.status == RequestStatus.PENDING


# ---------------------------------------------------------------------------
# §4.3 SLA tracking
# ---------------------------------------------------------------------------

class TestSLATracking:
    def test_export_request_overdue_when_past_deadline(self):
        from datetime import timedelta
        req = DataExportRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            sla_deadline=datetime.now(timezone.utc) - timedelta(days=1),
            status=RequestStatus.PENDING,
        )
        assert req.is_overdue() is True

    def test_export_request_not_overdue_when_completed(self):
        from datetime import timedelta
        req = DataExportRequest(
            learner_id=uuid.uuid4(),
            requested_by=uuid.uuid4(),
            sla_deadline=datetime.now(timezone.utc) - timedelta(days=1),
            status=RequestStatus.COMPLETED,
        )
        assert req.is_overdue() is False
