"""Comprehensive unit tests for POPIA Data Subject Rights domain models."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.domain.data_subject_rights import (
    DataExportRequest,
    ErasureRequest,
    CorrectionRequest,
    RestrictionRequest,
    RequestStatus,
    EXPORT_SLA_DAYS,
    ERASURE_SLA_DAYS,
)


class TestDataSubjectRightsModels:
    def test_sla_constants(self):
        assert EXPORT_SLA_DAYS == 30
        assert ERASURE_SLA_DAYS == 30

    def test_request_status_enums(self):
        assert RequestStatus.PENDING.value == "pending"
        assert RequestStatus.IN_PROGRESS.value == "in_progress"
        assert RequestStatus.COMPLETED.value == "completed"
        assert RequestStatus.REJECTED.value == "rejected"
        assert RequestStatus.EXPIRED.value == "expired"

    def test_data_export_request_overdue(self):
        lid = uuid.uuid4()
        gid = uuid.uuid4()

        # Not overdue (deadline in future)
        req_future = DataExportRequest(
            learner_id=lid,
            requested_by=gid,
            status=RequestStatus.PENDING,
            sla_deadline=datetime.now(timezone.utc) + timedelta(days=10),
        )
        assert req_future.is_overdue() is False

        # Overdue (deadline in past and status pending)
        req_past = DataExportRequest(
            learner_id=lid,
            requested_by=gid,
            status=RequestStatus.PENDING,
            sla_deadline=datetime.now(timezone.utc) - timedelta(days=2),
        )
        assert req_past.is_overdue() is True

        # Completed past deadline is not considered overdue
        req_completed = DataExportRequest(
            learner_id=lid,
            requested_by=gid,
            status=RequestStatus.COMPLETED,
            sla_deadline=datetime.now(timezone.utc) - timedelta(days=2),
        )
        assert req_completed.is_overdue() is False

    def test_erasure_request_defaults(self):
        lid = uuid.uuid4()
        gid = uuid.uuid4()
        req = ErasureRequest(
            learner_id=lid,
            requested_by=gid,
        )
        assert req.status == RequestStatus.PENDING
        assert req.learner_id == lid
        assert req.requested_by == gid

    def test_correction_request_defaults(self):
        lid = uuid.uuid4()
        gid = uuid.uuid4()
        req = CorrectionRequest(
            learner_id=lid,
            requested_by=gid,
            field_name="learner_name",
            old_value="Old Name",
            new_value="New Name",
        )
        assert req.field_name == "learner_name"
        assert req.status == RequestStatus.PENDING

    def test_restriction_request_defaults(self):
        lid = uuid.uuid4()
        gid = uuid.uuid4()
        req = RestrictionRequest(
            learner_id=lid,
            requested_by=gid,
            reason="Parent dispute over assessment score",
        )
        assert req.status == RequestStatus.PENDING
        assert "dispute" in req.reason
