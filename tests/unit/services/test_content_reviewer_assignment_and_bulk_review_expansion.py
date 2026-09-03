"""Comprehensive unit tests for Content Reviewer Assignment and Bulk Review governance guardrails."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.content_factory import ContentGenerationArtifact, ContentReviewAssignment
from app.services.content_bulk_review import (
    BulkReviewResult,
    ContentBulkReviewService,
    _value,
)
from app.services.content_reviewer_assignment import (
    OPEN_STATUSES,
    RESOLVED_STATUSES,
    ContentReviewerAssignmentService,
    ReviewerWorkload,
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

    def test_statuses_constants_and_value_helper(self):
        assert "assigned" in OPEN_STATUSES
        assert "in_review" in OPEN_STATUSES
        assert "approved" in RESOLVED_STATUSES
        assert "cancelled" in RESOLVED_STATUSES
        assert _value(SimpleNamespace(value="custom_status")) == "custom_status"
        assert _value("plain_str") == "plain_str"


class TestContentReviewerAssignmentService:
    @pytest.mark.asyncio
    async def test_assign_artifact_branches(self):
        service = ContentReviewerAssignmentService()
        session = AsyncMock()
        artifact_id = uuid.uuid4()

        # 1. Artifact not found -> LookupError
        session.get.return_value = None
        with pytest.raises(LookupError, match="not found"):
            await service.assign_artifact(session, artifact_id, "rev-1", "admin")

        # 2. Existing resolved assignment -> ValueError
        mock_artifact = SimpleNamespace(artifact_id=artifact_id, version_number=1)
        session.get.return_value = mock_artifact

        mock_existing_resolved = SimpleNamespace(status="approved")
        with patch.object(service, "_reviewer_assignment", return_value=mock_existing_resolved):
            with pytest.raises(ValueError, match="already completed or closed"):
                await service.assign_artifact(session, artifact_id, "rev-1", "admin")

        # 3. Existing open assignment -> updates fields and returns
        mock_existing_open = SimpleNamespace(
            status="assigned",
            assigned_by="old_admin",
            priority="low",
            due_by=None,
            reviewer_competencies=[],
        )
        with patch.object(service, "_reviewer_assignment", return_value=mock_existing_open):
            due = datetime.now(timezone.utc) + timedelta(days=2)
            updated = await service.assign_artifact(
                session, artifact_id, "rev-1", "admin", priority="high", due_by=due, competencies=["math"]
            )
            assert updated.assigned_by == "admin"
            assert updated.priority == "high"
            assert updated.due_by == due
            assert updated.reviewer_competencies == ["math"]
            session.flush.assert_called()

        # 4. New assignment creation
        with patch.object(service, "_reviewer_assignment", return_value=None):
            new_assign = await service.assign_artifact(
                session, artifact_id, "rev-2", "admin", priority="normal", idempotency_key="key-1"
            )
            assert new_assign.assigned_to == "rev-2"
            assert new_assign.status == "assigned"
            assert new_assign.idempotency_key == "key-1"
            session.add.assert_called()
            session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_assign_batch_and_unassign(self):
        service = ContentReviewerAssignmentService()
        session = AsyncMock()
        a1, a2 = uuid.uuid4(), uuid.uuid4()

        # assign_batch
        with patch.object(service, "assign_artifact", new_callable=AsyncMock) as mock_assign:
            mock_assign.side_effect = [
                SimpleNamespace(artifact_id=a1),
                SimpleNamespace(artifact_id=a2),
            ]
            batch = await service.assign_batch(session, [a1, a2], "rev-1", "admin")
            assert len(batch) == 2
            assert mock_assign.call_count == 2

        # unassign_artifact: not found -> LookupError
        with patch.object(service, "_open_assignment", return_value=None):
            with pytest.raises(LookupError, match="Open assignment"):
                await service.unassign_artifact(session, a1, "admin")

        # unassign_artifact: success cancellation
        mock_open = SimpleNamespace(status="assigned", resolved_at=None, completed_at=None)
        with patch.object(service, "_open_assignment", return_value=mock_open):
            res = await service.unassign_artifact(session, a1, "admin")
            assert res.status == "cancelled"
            assert res.resolved_at is not None
            session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_get_reviewer_workload_and_list_assignments(self):
        service = ContentReviewerAssignmentService()
        session = AsyncMock()

        # get_reviewer_workload
        now = datetime.now(timezone.utc)
        item_assigned = SimpleNamespace(status="assigned", due_by=now + timedelta(days=1), created_at=now)
        item_in_review_overdue = SimpleNamespace(status="in_review", due_by=now - timedelta(days=1), created_at=now)
        item_no_due_overdue = SimpleNamespace(status="assigned", due_by=None, created_at=now - timedelta(days=4))

        mock_exec_res = MagicMock()
        mock_exec_res.scalars.return_value.all.return_value = [
            item_assigned,
            item_in_review_overdue,
            item_no_due_overdue,
        ]
        session.execute.return_value = mock_exec_res

        workload = await service.get_reviewer_workload(session, "rev-1")
        assert workload.total_open == 3
        assert workload.assigned == 2
        assert workload.in_review == 1
        assert workload.overdue == 2

        # list_assignments
        mock_exec_res.scalars.return_value.all.return_value = [item_assigned]
        listed = await service.list_assignments(session, reviewer_id="rev-1", status="assigned", limit=10)
        assert len(listed) == 1


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
    async def test_bulk_reject_and_quarantine_and_assign(self):
        mock_session = AsyncMock()
        mock_lifecycle = AsyncMock()
        mock_assignment = AsyncMock()
        service = ContentBulkReviewService(
            lifecycle_service=mock_lifecycle,
            assignment_service=mock_assignment,
        )

        aid1, aid2 = uuid.uuid4(), uuid.uuid4()

        # 1. bulk_reject empty reason
        with pytest.raises(ValueError, match="Bulk rejection requires a reason"):
            await service.bulk_reject(mock_session, [aid1], reviewer_id="rev-1", reason="   ")

        # 2. bulk_reject batch limit exceeded
        with patch.dict(os.environ, {"CONTENT_REVIEW_BULK_REJECT_MAX": "1"}):
            with pytest.raises(ValueError, match="limited to 1 artifacts"):
                await service.bulk_reject(mock_session, [aid1, aid2], reviewer_id="rev-1", reason="Reason")

        # 3. bulk_reject success
        mock_lifecycle.reject_artifact.side_effect = [
            SimpleNamespace(artifact_id=aid1),
            SimpleNamespace(artifact_id=aid2),
        ]
        res_rej = await service.bulk_reject(mock_session, [aid1, aid2], reviewer_id="rev-1", reason="Quality failure")
        assert res_rej.status == "rejected"
        assert res_rej.artifact_ids == [aid1, aid2]

        # 4. bulk_quarantine empty reason vs success
        with pytest.raises(ValueError, match="Bulk quarantine requires a reason"):
            await service.bulk_quarantine(mock_session, [aid1], reviewer_id="rev-1", reason="   ")

        mock_lifecycle.quarantine_artifact.side_effect = [
            SimpleNamespace(artifact_id=aid1),
        ]
        res_quar = await service.bulk_quarantine(mock_session, [aid1], reviewer_id="rev-1", reason="Safety issue")
        assert res_quar.status == "quarantined"
        assert res_quar.artifact_ids == [aid1]

        # 5. bulk_assign success
        mock_assignment.assign_batch.return_value = [
            SimpleNamespace(artifact_id=aid1),
            SimpleNamespace(artifact_id=aid2),
        ]
        res_assign = await service.bulk_assign(mock_session, [aid1, aid2], reviewer_id="rev-1", assigned_by="admin")
        assert res_assign.status == "assigned"
        assert res_assign.artifact_ids == [aid1, aid2]
