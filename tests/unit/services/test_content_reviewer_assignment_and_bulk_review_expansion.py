"""Comprehensive unit tests for Content Reviewer Assignment and Bulk Review governance guardrails."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock
import pytest

from app.services.content_reviewer_assignment import (
    OPEN_STATUSES,
    RESOLVED_STATUSES,
    ReviewerWorkload,
)
from app.services.content_bulk_review import (
    BulkReviewResult,
    ContentBulkReviewService,
)


class TestReviewerAssignmentModels:
    def test_reviewer_workload_dataclass(self):
        workload = ReviewerWorkload(
            reviewer_id="rev-1",
            assigned=5,
            in_review=2,
            overdue=1,
            total_open=7,
        )
        assert workload.reviewer_id == "rev-1"
        assert workload.total_open == 7
        assert workload.overdue == 1

    def test_statuses_constants(self):
        assert "assigned" in OPEN_STATUSES
        assert "in_review" in OPEN_STATUSES
        assert "approved" in RESOLVED_STATUSES
        assert "cancelled" in RESOLVED_STATUSES


class TestBulkReviewServiceGovernance:
    def test_bulk_review_result_dataclass(self):
        aid = uuid.uuid4()
        res = BulkReviewResult(
            status="rejected",
            artifact_ids=[aid],
            errors=[],
            summary={"rejected": 1},
        )
        assert res.status == "rejected"
        assert len(res.artifact_ids) == 1
        assert res.summary["rejected"] == 1

    @pytest.mark.asyncio
    async def test_bulk_approve_is_forbidden_by_governance(self):
        mock_session = AsyncMock()
        service = ContentBulkReviewService()

        with pytest.raises(ValueError, match="Bulk approval is disabled by Phase 3 governance"):
            await service.bulk_approve(
                session=mock_session,
                artifact_ids=[uuid.uuid4()],
                reviewer_id="rev-1",
                notes="Looks good",
            )

    @pytest.mark.asyncio
    async def test_bulk_reject_empty_reason_raises(self):
        mock_session = AsyncMock()
        service = ContentBulkReviewService()

        with pytest.raises(ValueError, match="Bulk rejection requires a reason"):
            await service.bulk_reject(
                session=mock_session,
                artifact_ids=[uuid.uuid4()],
                reviewer_id="rev-1",
                reason="   ",
            )
