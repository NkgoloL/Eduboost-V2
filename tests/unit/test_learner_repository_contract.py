"""
tests/unit/test_learner_repository_contract.py
─────────────────────────────────────────────────────────────────────────────
Task 135A: LearnerRepository contract tests

Validates:
  - get_by_id() returns correct learner or None
  - delete_by_id() physically deletes learner (Right to Erasure)
  - soft_delete() marks learner as deleted with metadata
  - purge_personal_data() physically deletes learner record
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models import Learner
from app.repositories.learner_repository import LearnerRepository


class TestLearnerRepositoryGetById:

    @pytest.mark.asyncio
    async def test_get_by_id_returns_learner(self):
        """get_by_id() must return learner when it exists."""
        db = AsyncMock()
        learner_id = uuid.uuid4()

        learner = Learner(
            id=learner_id,
            display_name="Test Learner",
            grade=4,
            is_deleted=False,
        )

        # Mock the base repository get method
        repo = LearnerRepository(db)
        repo.get = AsyncMock(return_value=learner)

        result = await repo.get_by_id(learner_id)
        assert result is not None
        assert result.id == learner_id
        assert result.display_name == "Test Learner"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_missing(self):
        """get_by_id() must return None when learner does not exist."""
        db = AsyncMock()
        repo = LearnerRepository(db)
        repo.get = AsyncMock(return_value=None)

        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_accepts_string_id(self):
        """get_by_id() must accept string UUID."""
        db = AsyncMock()
        learner_id = uuid.uuid4()

        learner = Learner(
            id=learner_id,
            display_name="Test Learner",
            grade=4,
            is_deleted=False,
        )

        repo = LearnerRepository(db)
        repo.get = AsyncMock(return_value=learner)

        result = await repo.get_by_id(str(learner_id))
        assert result is not None
        assert result.id == learner_id


class TestLearnerRepositoryDeleteById:

    @pytest.mark.asyncio
    async def test_delete_by_id_physically_deletes(self):
        """delete_by_id() must physically delete learner record (Right to Erasure)."""
        db = AsyncMock()
        learner_id = uuid.uuid4()

        # Mock successful delete
        result_mock = MagicMock()
        result_mock.rowcount = 1
        db.execute = AsyncMock(return_value=result_mock)

        repo = LearnerRepository(db)
        deleted = await repo.delete_by_id(learner_id)

        assert deleted is True
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_by_id_returns_false_for_missing(self):
        """delete_by_id() must return False when learner does not exist."""
        db = AsyncMock()

        # Mock no rows affected
        result_mock = MagicMock()
        result_mock.rowcount = 0
        db.execute = AsyncMock(return_value=result_mock)

        repo = LearnerRepository(db)
        deleted = await repo.delete_by_id(uuid.uuid4())

        assert deleted is False


class TestLearnerRepositorySoftDelete:

    @pytest.mark.asyncio
    async def test_soft_delete_marks_learner_as_deleted(self):
        """soft_delete() must mark learner as deleted with metadata."""
        db = AsyncMock()
        learner_id = uuid.uuid4()

        learner = Learner(
            id=learner_id,
            display_name="Test Learner",
            grade=4,
            is_deleted=False,
        )

        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=learner)
        db.add = MagicMock()
        db.flush = AsyncMock()

        await repo.soft_delete(learner_id)

        assert learner.is_deleted is True
        assert learner.display_name == "[erased]"
        assert learner.deletion_requested_at is not None
        db.add.assert_called_once_with(learner)
        db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_soft_delete_noops_for_missing_learner(self):
        """soft_delete() must not raise when learner does not exist."""
        db = AsyncMock()

        repo = LearnerRepository(db)
        repo.get_by_id = AsyncMock(return_value=None)

        await repo.soft_delete(uuid.uuid4())  # Should not raise


class TestLearnerRepositoryPurgePersonalData:

    @pytest.mark.asyncio
    async def test_purge_personal_data_physically_deletes(self):
        """purge_personal_data() must physically delete learner record."""
        db = AsyncMock()
        learner_id = uuid.uuid4()

        repo = LearnerRepository(db)
        db.execute = AsyncMock()

        await repo.purge_personal_data(learner_id)

        db.execute.assert_awaited_once()
