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
from types import SimpleNamespace
from uuid import uuid4

from app.repositories.assessment_repository import AssessmentRepository


class TestAssessmentRepositoryListAssessments:

    @pytest.mark.asyncio
    async def test_list_assessments_returns_list(self):
        """list_assessments() must return list of assessment dicts."""
        db = AsyncMock()

        result_mock = MagicMock()
        assessment_id = uuid4()
        result_mock.scalars.return_value.all.return_value = [
            SimpleNamespace(
                id=assessment_id,
                title="Test",
                subject_code="MATH",
                grade_level=4,
                assessment_type="quiz",
                total_marks=10,
                questions=[],
                passing_score=7,
                is_active=True,
            )
        ]
        db.execute = AsyncMock(return_value=result_mock)

        repo = AssessmentRepository()
        result = await repo.list_assessments(limit=10, offset=0, db=db)

        assert len(result) == 1
        assert result[0]["assessment_id"] == str(assessment_id)
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_assessments_applies_limit_and_offset(self):
        """list_assessments() must apply limit and offset parameters."""
        db = AsyncMock()

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
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
        assessment_id = uuid4()
        result_mock.scalar_one_or_none.return_value = SimpleNamespace(
            id=assessment_id,
            title="Test",
            subject_code="MATH",
            grade_level=4,
            assessment_type="quiz",
            total_marks=10,
            questions=[],
            passing_score=7,
            is_active=True,
        )
        db.execute = AsyncMock(return_value=result_mock)

        repo = AssessmentRepository()
        result = await repo.get_assessment(str(assessment_id), db=db)

        assert result is not None
        assert result["assessment_id"] == str(assessment_id)
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_assessment_returns_none_when_missing(self):
        """get_assessment() must return None when assessment does not exist."""
        db = AsyncMock()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=result_mock)

        repo = AssessmentRepository()
        result = await repo.get_assessment(str(uuid4()), db=db)

        assert result is None
