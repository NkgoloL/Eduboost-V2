from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import popia_service
from app.services.popia_service import (
    POPIA_ERASURE_GRACE_DAYS,
    POPIA_ERASURE_REVIEW_SLA_DAYS,
    POPIA_EXPORT_SLA_DAYS,
    POPIADataRightsService,
    RightsRequestStatus,
)


@pytest.mark.unit
def test_popia_service_init_stores_dependencies():
    """Verify constructor stores database session and repositories."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    assert service.db is db
    assert service.learners is not None
    assert service.audit is not None
    assert service.consent is not None


class FakeService(POPIADataRightsService):
    def __init__(self, learner):
        self.learner = learner

    async def load_learner_for_read(self, learner_id, current_user):
        return self.learner

    async def load_learner_for_write(self, learner_id, current_user):
        return self.learner


@pytest.mark.asyncio
async def test_erasure_requires_guardian_or_admin() -> None:
    svc = FakeService(SimpleNamespace(id="learner-1", guardian_id="guardian-1", deletion_requested_at=None))
    with pytest.raises(HTTPException) as exc:
        await svc.request_erasure("learner-1", {"sub": "guardian-2", "role": "parent"})
    assert exc.value.status_code == 403


@pytest.mark.unit
def test_popia_constants_defined():
    """Verify POPIA SLA constants are defined correctly."""
    assert POPIA_EXPORT_SLA_DAYS == 30
    assert POPIA_ERASURE_REVIEW_SLA_DAYS == 30
    assert POPIA_ERASURE_GRACE_DAYS == 30


@pytest.mark.unit
def test_rights_request_status_dataclass():
    """Verify RightsRequestStatus dataclass is properly defined."""
    status = RightsRequestStatus(
        request_type="export",
        status="completed",
        learner_id="learner-123",
        requested_at="2024-01-01T00:00:00Z",
        due_at="2024-01-31T00:00:00Z",
        audit_event_type="data_export.requested",
        requires_admin_review=False,
        reason="user_request",
    )
    assert status.request_type == "export"
    assert status.status == "completed"
    assert status.learner_id == "learner-123"
    assert status.requires_admin_review is False
    assert status.reason == "user_request"


@pytest.mark.unit
def test_rights_request_status_defaults():
    """Verify RightsRequestStatus has correct defaults."""
    status = RightsRequestStatus(
        request_type="export",
        status="completed",
        learner_id="learner-123",
        requested_at="2024-01-01T00:00:00Z",
        due_at="2024-01-31T00:00:00Z",
        audit_event_type="data_export.requested",
    )
    assert status.requires_admin_review is False
    assert status.reason is None


@pytest.mark.unit
def test_to_csv_converts_payload():
    """Verify _to_csv converts payload to CSV format."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    payload = {
        "learner": {"id": "learner-123", "name": "Test"},
        "diagnostic_sessions": [{"id": "session-1", "theta": 0.5}],
        "guardian": {"id": "guardian-1", "email": "test@example.com"},
    }
    csv_output = service._to_csv(payload)
    assert "learner,id,learner-123" in csv_output
    assert "learner,name,Test" in csv_output
    assert "diagnostic_sessions,id,session-1" in csv_output
    assert "guardian,id,guardian-1" in csv_output


@pytest.mark.unit
def test_status_creates_rights_request_status():
    """Verify _status creates RightsRequestStatus with correct values."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    with patch("app.services.popia_service._now") as mock_now:
        mock_now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_now.return_value.__add__ = lambda self, days: SimpleNamespace(isoformat=lambda: "2024-01-31T00:00:00Z")
        status = service._status("export", "completed", "learner-123", 30, "data_export.requested")
        assert status.request_type == "export"
        assert status.status == "completed"
        assert status.learner_id == "learner-123"
        assert status.audit_event_type == "data_export.requested"


@pytest.mark.unit
def test_status_with_optional_params():
    """Verify _status handles optional parameters."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    with patch("app.services.popia_service._now") as mock_now:
        mock_now.return_value.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_now.return_value.__add__ = lambda self, days: SimpleNamespace(isoformat=lambda: "2024-01-31T00:00:00Z")
        status = service._status(
            "restriction",
            "accepted",
            "learner-123",
            30,
            "processing.restricted",
            requires_admin_review=True,
            reason="user_request",
        )
        assert status.requires_admin_review is True
        assert status.reason == "user_request"


@pytest.mark.unit
async def test_requires_admin_review_returns_false():
    """Verify requires_admin_review returns False (current policy)."""
    db = AsyncMock()
    service = POPIADataRightsService(db)
    learner = SimpleNamespace(id="learner-123")
    result = await service.requires_admin_review(learner)
    assert result is False


@pytest.mark.unit
def test_now_returns_utc_datetime():
    """Verify _now returns UTC datetime."""
    result = popia_service._now()
    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc


@pytest.mark.unit
def test_iso_returns_isoformat_string():
    """Verify _iso returns ISO format string for datetime."""
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = popia_service._iso(dt)
    assert result == "2024-01-01T12:00:00+00:00"


@pytest.mark.unit
def test_iso_returns_none_for_none():
    """Verify _iso returns None for None input."""
    result = popia_service._iso(None)
    assert result is None


@pytest.mark.unit
def test_module_exports_all_public_symbols():
    """Verify __all__ contains expected public symbols."""
    expected = {
        "POPIADataRightsService",
        "POPIA_ERASURE_GRACE_DAYS",
        "POPIA_ERASURE_REVIEW_SLA_DAYS",
        "POPIA_EXPORT_SLA_DAYS",
        "RightsRequestStatus",
    }
    assert set(popia_service.__all__) == expected


@pytest.mark.asyncio
async def test_request_correction_with_allowed_fields():
    """Verify request_correction updates allowed fields."""
    db = AsyncMock()
    POPIADataRightsService(db)
    learner = SimpleNamespace(id="learner-123", display_name="Old Name", grade=4, language="en")

    class FakeService(POPIADataRightsService):
        def __init__(self, learner, audit_mock):
            self.learner = learner
            self.audit = audit_mock
            self.db = db

        async def load_learner_for_write(self, learner_id, current_user):
            return self.learner

    audit_mock = AsyncMock()
    fake_service = FakeService(learner, audit_mock)

    result = await fake_service.request_correction(
        "learner-123",
        {"sub": "guardian-1"},
        fields={"display_name": "New Name", "grade": 5},
        reason="typo_fix"
    )

    assert learner.display_name == "New Name"
    assert learner.grade == 5
    assert result["request_type"] == "correction"
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_request_correction_rejects_unsupported_fields():
    """Verify request_correction raises on unsupported fields."""
    db = AsyncMock()
    POPIADataRightsService(db)
    learner = SimpleNamespace(id="learner-123")

    class FakeService(POPIADataRightsService):
        def __init__(self, learner):
            self.learner = learner

        async def load_learner_for_write(self, learner_id, current_user):
            return self.learner

    fake_service = FakeService(learner)

    with pytest.raises(HTTPException) as exc:
        await fake_service.request_correction(
            "learner-123",
            {"sub": "guardian-1"},
            fields={"unsupported_field": "value"},
            reason="test"
        )
    assert exc.value.status_code == 422
    assert "unsupported_fields" in exc.value.detail


@pytest.mark.asyncio
async def test_restrict_processing_calls_consent_revoke():
    """Verify restrict_processing calls consent.revoke."""
    db = AsyncMock()
    POPIADataRightsService(db)
    learner = SimpleNamespace(id="learner-123", pseudonym_id="pseudo-123")
    consent_mock = AsyncMock()
    audit_mock = AsyncMock()

    class FakeService(POPIADataRightsService):
        def __init__(self, learner, consent_mock, audit_mock, db):
            self.learner = learner
            self.consent = consent_mock
            self.audit = audit_mock
            self.db = db

        async def load_learner_for_write(self, learner_id, current_user):
            return self.learner

    fake_service = FakeService(learner, consent_mock, audit_mock, db)

    await fake_service.restrict_processing(
        "learner-123",
        {"sub": "guardian-1"},
        reason="user_request"
    )

    consent_mock.revoke.assert_called_once_with(
        "learner-123",
        guardian_id="guardian-1",
        reason="processing_restricted"
    )


@pytest.mark.asyncio
async def test_cancel_erasure_restores_learner():
    """Verify cancel_erasure restores learner and updates state."""
    db = AsyncMock()
    erasure_request = SimpleNamespace(
        id="erasure-1",
        requester_id="guardian-1",
        state="requested"
    )
    learner = SimpleNamespace(
        id="learner-123",
        pseudonym_id="pseudo-123",
        is_deleted=True,
        deletion_requested_at=datetime.now(timezone.utc),
        display_name="[erased]"
    )
    audit_mock = AsyncMock()

    class FakeService(POPIADataRightsService):
        def __init__(self, learner, erasure_request, audit_mock, db):
            self.learner = learner
            self._erasure_request = erasure_request
            self.audit = audit_mock
            self.db = db

        async def load_learner_for_write(self, learner_id, current_user):
            return self.learner

    fake_service = FakeService(learner, erasure_request, audit_mock, db)
    db.scalar.return_value = erasure_request

    result = await fake_service.cancel_erasure("learner-123", {"sub": "guardian-1"})

    assert learner.is_deleted is False
    assert learner.deletion_requested_at is None
    assert learner.display_name == "Restored"
    assert result["state"] == "cancelled"


@pytest.mark.asyncio
async def test_build_learner_export_json_returns_payload_and_status():
    """Verify build_learner_export returns JSON payload and logs audit."""
    db = AsyncMock()
    audit_mock = AsyncMock()
    consent_mock = AsyncMock()

    learner = SimpleNamespace(id="learner-123", pseudonym_id="pseudo-123")

    class FakeService(POPIADataRightsService):
        def __init__(self, db, learner, audit_mock, consent_mock):
            self.db = db
            self.learner = learner
            self.audit = audit_mock
            self.consent = consent_mock

        async def load_learner_for_read(self, learner_id, current_user):
            return self.learner

        async def _export_payload(self, learner):
            return {"learner": {"id": learner.pseudonym_id}}

    svc = FakeService(db, learner, audit_mock, consent_mock)

    with patch("app.services.popia_service._now") as mock_now:
        mock_now.return_value.strftime.return_value = "20240101_120000"
        result = await svc.build_learner_export(
            "learner-123",
            {"sub": "guardian-1"},
            export_format="json",
        )

    assert result["content_type"] == "application/json"
    assert result["filename"].endswith(".json")
    assert result["data"] == {"learner": {"id": "pseudo-123"}}
    # status is a dict with request_type and audit_event_type
    assert result["status"]["request_type"] == "export"
    assert result["status"]["audit_event_type"] == "data_export.requested"
    audit_mock.append.assert_called_once()


@pytest.mark.asyncio
async def test_build_learner_export_csv_branch():
    """Verify build_learner_export handles CSV branch and _to_csv output."""
    db = AsyncMock()
    audit_mock = AsyncMock()
    consent_mock = AsyncMock()

    learner = SimpleNamespace(id="learner-123", pseudonym_id="pseudo-123")

    class FakeService(POPIADataRightsService):
        def __init__(self, db, learner, audit_mock, consent_mock):
            self.db = db
            self.learner = learner
            self.audit = audit_mock
            self.consent = consent_mock

        async def load_learner_for_read(self, learner_id, current_user):
            return self.learner

        async def _export_payload(self, learner):
            return {"learner": {"id": learner.pseudonym_id, "name": "Test"}}

    svc = FakeService(db, learner, audit_mock, consent_mock)

    with patch("app.services.popia_service._now") as mock_now:
        mock_now.return_value.strftime.return_value = "20240101_120000"
        result = await svc.build_learner_export(
            "learner-123",
            {"sub": "guardian-1"},
            export_format="csv",
        )

    assert result["content_type"] == "text/csv"
    assert result["filename"].endswith(".csv")
    assert isinstance(result["data"], str)
    # CSV header present and learner id row included
    assert "section,field,value" in result["data"].splitlines()[0]
    assert "learner,id,pseudo-123" in result["data"]
    audit_mock.append.assert_called_once()


@pytest.mark.asyncio
async def test_postflight_erasure_verification_physical_deleted():
    """Verify postflight verification passes when learner fully deleted (physical)."""
    db = AsyncMock()
    svc = POPIADataRightsService(db)
    # Mock learners repo on service
    svc.learners = SimpleNamespace(get_by_id=AsyncMock(return_value=None))
    # Any scalar return indicates audit records preserved
    db.scalar = AsyncMock(return_value=SimpleNamespace(id="evt-1"))

    result = await svc._postflight_erasure_verification("learner-123", method="physical")

    assert result["learner_record_deleted"] is True
    assert result["dependent_records_deleted"] is True
    assert result["pii_not_retrievable"] is True
    assert result["all_checks_passed"] is True


@pytest.mark.asyncio
async def test_postflight_erasure_verification_soft_marked_erased():
    """Verify postflight verification for soft delete retains record but marks erased."""
    db = AsyncMock()
    svc = POPIADataRightsService(db)
    # Soft-deleted learner remains but is flagged and display_name is placeholder
    soft_learner = SimpleNamespace(is_deleted=True, display_name="[erased]")
    svc.learners = SimpleNamespace(get_by_id=AsyncMock(return_value=soft_learner))
    db.scalar = AsyncMock(return_value=None)

    result = await svc._postflight_erasure_verification("learner-123", method="soft")

    assert result["learner_record_deleted"] is False
    assert result["dependent_records_deleted"] is True
    assert result["pii_not_retrievable"] is True
    # all_checks_passed requires full deletion; for soft delete this is False
    assert result["all_checks_passed"] is False


@pytest.mark.asyncio
async def test_request_erasure_creates_request_and_soft_deletes_learner():
    """Verify request_erasure creates erasure request and soft deletes learner."""
    db = AsyncMock()
    db.scalar = AsyncMock(return_value=None)  # No existing request
    db.add = MagicMock()
    db.flush = AsyncMock()

    learner = SimpleNamespace(
        id="learner-123",
        guardian_id="guardian-1",
        pseudonym_id="pseudo-123"
    )
    consent_mock = AsyncMock()
    audit_mock = AsyncMock()

    class FakeService(POPIADataRightsService):
        def __init__(self, db, learner, consent_mock, audit_mock):
            self.db = db
            self.learner = learner
            self.consent = consent_mock
            self.audit = audit_mock

        async def load_learner_for_write(self, learner_id, current_user):
            return self.learner

        async def _preflight_erasure_checks(self, learner, requester_id, requester_role):
            return {"all_checks_passed": True, "legal_hold": False}

    svc = FakeService(db, learner, consent_mock, audit_mock)

    result = await svc.request_erasure("learner-123", {"sub": "guardian-1"})

    assert learner.is_deleted is True
    assert learner.display_name == "[erased]"
    assert learner.deletion_requested_at is not None
    assert result["state"] == "requested"
    assert result["learner_id"] == "learner-123"
    consent_mock.execute_erasure.assert_called_once()
    audit_mock.append.assert_called_once()
    db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_request_erasure_raises_on_existing_request():
    """Verify request_erasure raises when erasure request already exists."""
    db = AsyncMock()
    existing_request = SimpleNamespace(id="erasure-1")
    db.scalar = AsyncMock(return_value=existing_request)

    learner = SimpleNamespace(id="learner-123", guardian_id="guardian-1")

    class FakeService(POPIADataRightsService):
        def __init__(self, db, learner):
            self.db = db
            self.learner = learner

        async def load_learner_for_write(self, learner_id, current_user):
            return self.learner

    svc = FakeService(db, learner)

    with pytest.raises(HTTPException) as exc:
        await svc.request_erasure("learner-123", {"sub": "guardian-1"})
    assert exc.value.status_code == 409
    assert "already in progress" in exc.value.detail


@pytest.mark.asyncio
async def test_cancel_erasure_raises_on_no_active_request():
    """Verify cancel_erasure raises when no active erasure request exists."""
    db = AsyncMock()
    db.scalar = AsyncMock(return_value=None)

    learner = SimpleNamespace(id="learner-123", guardian_id="guardian-1")

    class FakeService(POPIADataRightsService):
        def __init__(self, db, learner):
            self.db = db
            self.learner = learner

        async def load_learner_for_write(self, learner_id, current_user):
            return self.learner

    svc = FakeService(db, learner)

    with pytest.raises(HTTPException) as exc:
        await svc.cancel_erasure("learner-123", {"sub": "guardian-1"})
    assert exc.value.status_code == 409
    assert "No active erasure request" in exc.value.detail
