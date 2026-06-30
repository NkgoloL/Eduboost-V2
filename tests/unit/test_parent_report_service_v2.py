"""tests/unit/test_parent_report_service_v2.py
Unit tests for ParentReportServiceV2 report generation.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.parent_report_service_v2 import ParentReportServiceV2


@pytest.mark.unit
async def test_build_report_raises_when_learner_not_found():
    """Verify build_report raises ValueError when learner not found."""
    mock_learner_repo = AsyncMock()
    mock_learner_repo.get_by_id = AsyncMock(return_value=None)
    mock_report_repo = AsyncMock()
    service = ParentReportServiceV2(mock_learner_repo, mock_report_repo)

    with pytest.raises(ValueError, match="Learner not found"):
        await service.build_report("learner-123", "guardian-456")


@pytest.mark.unit
async def test_build_report_raises_when_guardian_not_linked():
    """Verify build_report raises PermissionError when guardian not linked."""
    mock_learner = MagicMock()
    mock_learner_repo = AsyncMock()
    mock_learner_repo.get_by_id = AsyncMock(return_value=mock_learner)
    mock_report_repo = AsyncMock()
    mock_report_repo.verify_guardian_link = AsyncMock(return_value=False)
    service = ParentReportServiceV2(mock_learner_repo, mock_report_repo)

    with pytest.raises(PermissionError, match="Guardian is not linked"):
        await service.build_report("learner-123", "guardian-456")


@pytest.mark.unit
async def test_build_report_generates_summary_with_weak_subjects():
    """Verify build_report generates priority summary for weak subjects."""
    mock_learner = MagicMock()
    mock_learner_repo = AsyncMock()
    mock_learner_repo.get_by_id = AsyncMock(return_value=mock_learner)
    mock_report_repo = AsyncMock()
    mock_report_repo.verify_guardian_link = AsyncMock(return_value=True)
    mock_report_repo.get_subject_mastery = AsyncMock(return_value=[
        {"subject_code": "MAT", "mastery_score": 0.3},
        {"subject_code": "ENG", "mastery_score": 0.7},
    ])
    mock_report_repo.persist_report = AsyncMock(return_value="report-123")
    service = ParentReportServiceV2(mock_learner_repo, mock_report_repo)

    with patch("app.services.parent_report_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.build_report("learner-123", "guardian-456")

        assert result["report_id"] == "report-123"
        assert "Priority support needed" in result["summary"]
        assert "MAT" in result["summary"]


@pytest.mark.unit
async def test_build_report_generates_steady_summary():
    """Verify build_report generates steady summary when no weak subjects."""
    mock_learner = MagicMock()
    mock_learner_repo = AsyncMock()
    mock_learner_repo.get_by_id = AsyncMock(return_value=mock_learner)
    mock_report_repo = AsyncMock()
    mock_report_repo.verify_guardian_link = AsyncMock(return_value=True)
    mock_report_repo.get_subject_mastery = AsyncMock(return_value=[
        {"subject_code": "MAT", "mastery_score": 0.8},
        {"subject_code": "ENG", "mastery_score": 0.9},
    ])
    mock_report_repo.persist_report = AsyncMock(return_value="report-123")
    service = ParentReportServiceV2(mock_learner_repo, mock_report_repo)

    with patch("app.services.parent_report_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.build_report("learner-123", "guardian-456")

        assert result["summary"] == "Learner is progressing steadily."


@pytest.mark.unit
async def test_list_reports_raises_when_guardian_not_linked():
    """Verify list_reports raises PermissionError when guardian not linked."""
    mock_learner_repo = AsyncMock()
    mock_report_repo = AsyncMock()
    mock_report_repo.verify_guardian_link = AsyncMock(return_value=False)
    service = ParentReportServiceV2(mock_learner_repo, mock_report_repo)

    with pytest.raises(PermissionError, match="Guardian is not linked"):
        await service.list_reports("learner-123", "guardian-456")


@pytest.mark.unit
async def test_list_reports_returns_reports():
    """Verify list_reports returns reports when guardian is linked."""
    mock_learner_repo = AsyncMock()
    mock_report_repo = AsyncMock()
    mock_report_repo.verify_guardian_link = AsyncMock(return_value=True)
    mock_report_repo.get_reports_for_learner = AsyncMock(return_value=[
        {"report_id": "report-1", "summary": "Test 1"},
        {"report_id": "report-2", "summary": "Test 2"},
    ])
    service = ParentReportServiceV2(mock_learner_repo, mock_report_repo)

    result = await service.list_reports("learner-123", "guardian-456")

    assert len(result) == 2
    assert result[0]["report_id"] == "report-1"
