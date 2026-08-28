"""Comprehensive unit tests for GuardianRepository, LearnerRepository, and ConsentRepository."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.repositories.repositories import (
    GuardianRepository,
    LearnerRepository,
    ConsentRepository,
)


class TestGuardianRepository:
    def test_init(self):
        mock_db = AsyncMock()
        repo = GuardianRepository(db=mock_db)
        assert repo.db == mock_db

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_res

        repo = GuardianRepository(db=mock_db)
        res = await repo.get_by_id("g-123")
        assert res is not None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_email_hash(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_res

        repo = GuardianRepository(db=mock_db)
        res = await repo.get_by_email_hash("hash-abc")
        assert res is not None
        mock_db.execute.assert_called_once()


class TestLearnerRepository:
    @pytest.mark.asyncio
    async def test_get_by_id(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_res

        repo = LearnerRepository(db=mock_db)
        res = await repo.get_by_id("l-456")
        assert res is not None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_guardian(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalars.return_value.all.return_value = [MagicMock()]
        mock_db.execute.return_value = mock_res

        repo = LearnerRepository(db=mock_db)
        res = await repo.get_by_guardian("g-123", skip=0, limit=10)
        assert len(res) == 1


class TestConsentRepository:
    @pytest.mark.asyncio
    async def test_get_latest_for_learner(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_res

        repo = ConsentRepository(db=mock_db)
        res = await repo.get_latest_for_learner("l-456")
        assert res is not None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.rowcount = 1
        mock_db.execute.return_value = mock_res

        repo = ConsentRepository(db=mock_db)
        count = await repo.revoke("l-456")
        assert count == 1
        mock_db.execute.assert_called_once()
