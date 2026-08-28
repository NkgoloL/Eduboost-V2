"""Comprehensive unit tests for ScopeReviewEvidenceStatus data model and review evidence status."""
from __future__ import annotations

import pytest

from app.services.content_file_review_workflow import ScopeReviewEvidenceStatus


class TestContentFileReviewWorkflow:
    def test_scope_review_evidence_status_dataclass(self):
        status = ScopeReviewEvidenceStatus(
            scope_id="grade4_mathematics_en",
            status="pending",
            approved=False,
            stage_unlocked=False,
            production_unlocked=False,
            blockers=["Pending human review"],
            stage_blockers=["Pending reviewer assignment"],
            production_blockers=["Pending legal signoff"],
            manifest_path=None,
            manifest=None,
        )
        assert status.scope_id == "grade4_mathematics_en"
        assert status.approved is False
        assert status.stage_unlocked is False
        assert len(status.blockers) == 1
        assert len(status.stage_blockers) == 1
        assert len(status.production_blockers) == 1

    def test_scope_review_evidence_status_approved_state(self):
        status = ScopeReviewEvidenceStatus(
            scope_id="grade4_mathematics_en",
            status="approved",
            approved=True,
            stage_unlocked=True,
            production_unlocked=True,
            blockers=[],
            stage_blockers=[],
            production_blockers=[],
            manifest_path=None,
            manifest={"decision": "approved"},
        )
        assert status.approved is True
        assert status.stage_unlocked is True
        assert status.production_unlocked is True
        assert len(status.blockers) == 0
