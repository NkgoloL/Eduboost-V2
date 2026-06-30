"""
tests/unit/test_mastery_repository_contract.py
─────────────────────────────────────────────────────────────────────────────
Task 135A: MasteryRepository contract tests

Validates:
  - upsert_topic_mastery() creates or updates topic mastery
  - get_topic_mastery() returns topic mastery or None
  - list_topic_mastery_by_learner() returns all topic mastery for learner
  - create_snapshot() creates mastery snapshot
  - get_snapshots_for_learner_topic() returns snapshots for learner/topic
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models import TopicMastery, MasterySnapshot
from app.repositories.mastery_repository import MasteryRepository


class TestMasteryRepositoryUpsertTopicMastery:

    @pytest.mark.asyncio
    async def test_upsert_creates_new_topic_mastery(self):
        """upsert_topic_mastery() must create new topic mastery when none exists."""
        db = AsyncMock()
        learner_id = uuid.uuid4()
        caps_ref = "MATH:4:FRACTIONS"

        repo = MasteryRepository(db)
        repo.get_topic_mastery = AsyncMock(return_value=None)
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()

        result = await repo.upsert_topic_mastery(
            learner_id=learner_id,
            caps_ref=caps_ref,
            mastery_score=0.8,
            mastery_label="proficient",
        )

        assert result is not None
        db.add.assert_called_once()
        db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_upsert_updates_existing_topic_mastery(self):
        """upsert_topic_mastery() must update existing topic mastery."""
        db = AsyncMock()
        learner_id = uuid.uuid4()
        caps_ref = "MATH:4:FRACTIONS"

        existing = TopicMastery(
            learner_id=str(learner_id),
            caps_ref=caps_ref,
            mastery_score=0.5,
            mastery_label="developing",
        )

        repo = MasteryRepository(db)
        repo.get_topic_mastery = AsyncMock(return_value=existing)
        db.flush = AsyncMock()
        db.refresh = AsyncMock()

        result = await repo.upsert_topic_mastery(
            learner_id=learner_id,
            caps_ref=caps_ref,
            mastery_score=0.8,
            mastery_label="proficient",
        )

        assert result.mastery_score == 0.8
        assert result.mastery_label == "proficient"
        db.add.assert_not_called()
        db.flush.assert_awaited_once()


class TestMasteryRepositoryGetTopicMastery:

    @pytest.mark.asyncio
    async def test_get_topic_mastery_returns_mastery(self):
        """get_topic_mastery() must return topic mastery when it exists."""
        db = AsyncMock()
        learner_id = uuid.uuid4()
        caps_ref = "MATH:4:FRACTIONS"

        mastery = TopicMastery(
            learner_id=str(learner_id),
            caps_ref=caps_ref,
            mastery_score=0.8,
            mastery_label="proficient",
        )

        result_mock = MagicMock()
        result_mock.scalar_one_or_none = MagicMock(return_value=mastery)
        db.execute = AsyncMock(return_value=result_mock)

        repo = MasteryRepository(db)
        result = await repo.get_topic_mastery(learner_id, caps_ref)

        assert result is not None
        assert result.caps_ref == caps_ref
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_topic_mastery_returns_none_when_missing(self):
        """get_topic_mastery() must return None when mastery does not exist."""
        db = AsyncMock()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none = MagicMock(return_value=None)
        db.execute = AsyncMock(return_value=result_mock)

        repo = MasteryRepository(db)
        result = await repo.get_topic_mastery(uuid.uuid4(), "MATH:4:FRACTIONS")

        assert result is None


class TestMasteryRepositoryListTopicMasteryByLearner:

    @pytest.mark.asyncio
    async def test_list_topic_mastery_by_learner_returns_list(self):
        """list_topic_mastery_by_learner() must return all topic mastery for learner."""
        db = AsyncMock()
        learner_id = uuid.uuid4()

        mastery1 = TopicMastery(
            learner_id=str(learner_id),
            caps_ref="MATH:4:FRACTIONS",
            mastery_score=0.8,
            mastery_label="proficient",
        )

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [mastery1]
        db.execute = AsyncMock(return_value=result_mock)

        repo = MasteryRepository(db)
        result = await repo.list_topic_mastery_by_learner(learner_id)

        assert len(result) == 1
        assert result[0].learner_id == str(learner_id)
        db.execute.assert_awaited_once()


class TestMasteryRepositoryCreateSnapshot:

    @pytest.mark.asyncio
    async def test_create_snapshot_persists_snapshot(self):
        """create_snapshot() must persist mastery snapshot."""
        db = AsyncMock()
        learner_id = uuid.uuid4()
        caps_ref = "MATH:4:FRACTIONS"

        repo = MasteryRepository(db)
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()

        result = await repo.create_snapshot(
            learner_id=learner_id,
            caps_ref=caps_ref,
            mastery_score=0.8,
            mastery_label="proficient",
            theta_estimate=0.5,
            theta_se=0.1,
            trigger="diagnostic",
        )

        assert result is not None
        db.add.assert_called_once()
        db.flush.assert_awaited_once()


class TestMasteryRepositoryGetSnapshotsForLearnerTopic:

    @pytest.mark.asyncio
    async def test_get_snapshots_returns_snapshots(self):
        """get_snapshots_for_learner_topic() must return snapshots for learner/topic."""
        db = AsyncMock()
        learner_id = uuid.uuid4()
        caps_ref = "MATH:4:FRACTIONS"

        snapshot = MasterySnapshot(
            learner_id=str(learner_id),
            caps_ref=caps_ref,
            mastery_score=0.8,
            mastery_label="proficient",
            theta_estimate=0.5,
            theta_se=0.1,
            trigger="diagnostic",
        )

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [snapshot]
        db.execute = AsyncMock(return_value=result_mock)

        repo = MasteryRepository(db)
        result = await repo.get_snapshots_for_learner_topic(learner_id, caps_ref)

        assert len(result) == 1
        assert result[0].learner_id == str(learner_id)
        db.execute.assert_awaited_once()
