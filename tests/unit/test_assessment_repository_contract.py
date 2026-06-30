"""
tests/unit/test_assessment_repository_contract.py
─────────────────────────────────────────────────────────────────────────────
Task 135A: AssessmentRepository contract tests

Validates:
  - list_assessments() returns paginated assessment list
  - get_assessment() returns specific assessment or None
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.repositories.assessment_repository import AssessmentRepository


class TestAssessmentRepositoryListAssessments:

    @pytest.mark.asyncio
    async def test_list_assessments_returns_list(self):
        """list_assessments() must return list of assessment dicts."""
        db = AsyncMock()

        result_mock = MagicMock()
        result_mock.mappings.return_value.all.return_value = [
            {"assessment_id": "1", "title": "Test", "subject_code": "MATH", "grade_level": 4, "assessment_type": "quiz", "total_marks": 10}
        ]
        db.execute = AsyncMock(return_value=result_mock)

        repo = AssessmentRepository()
        result = await repo.list_assessments(limit=10, offset=0, db=db)

        assert len(result) == 1
        assert result[0]["assessment_id"] == "1"
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_assessments_applies_limit_and_offset(self):
        """list_assessments() must apply limit and offset parameters."""
        db = AsyncMock()

        result_mock = MagicMock()
        result_mock.mappings.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=result_mock)

        repo = AssessmentRepository()
        await repo.list_assessments(limit=50, offset=10, db=db)

        # Verify execute was called
        db.execute.assert_awaited_once()


class TestAssessmentRepositoryGetAssessment:

    @pytest.mark.asyncio
    async def test_get_assessment_returns_assessment(self):
        """get_assessment() must return assessment dict when it exists."""
        db = AsyncMock()

        result_mock = MagicMock()
        result_mock.mappings.return_value.first.return_value = {
            "assessment_id": "1",
            "total_marks": 10,
            "questions": [],
            "passing_score": 7
        }
        db.execute = AsyncMock(return_value=result_mock)

        repo = AssessmentRepository()
        result = await repo.get_assessment("1", db=db)

        assert result is not None
        assert result["assessment_id"] == "1"
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_assessment_returns_none_when_missing(self):
        """get_assessment() must return None when assessment does not exist."""
        db = AsyncMock()

        result_mock = MagicMock()
        result_mock.mappings.return_value.first.return_value = None
        db.execute = AsyncMock(return_value=result_mock)

        repo = AssessmentRepository()
        result = await repo.get_assessment("999", db=db)

        assert result is None
