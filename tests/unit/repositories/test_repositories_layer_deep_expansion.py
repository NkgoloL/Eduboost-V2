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


class TestParentReportRepository:
    @pytest.mark.asyncio
    async def test_parent_report_repository_all_methods(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from app.repositories.parent_report_repository import ParentReportRepository

        repo = ParentReportRepository()
        mock_session = AsyncMock()
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value = mock_session
        mock_ctx.__aexit__.return_value = None

        with patch("app.repositories.parent_report_repository.AsyncSessionFactory", return_value=mock_ctx):
            # 1. verify_guardian_link
            mock_res1 = MagicMock()
            mock_res1.scalar_one_or_none.return_value = SimpleNamespace(id="consent-1")
            mock_session.execute.return_value = mock_res1
            assert await repo.verify_guardian_link("l-1", "g-1") is True

            # 2. get_subject_mastery
            mock_res2 = MagicMock()
            mock_row = SimpleNamespace(
                subject_code="MATH",
                mastery_score=0.85,
                grade_level=4,
                knowledge_gaps=["gap-1"],
            )
            mock_res2.scalars.return_value.all.return_value = [mock_row]
            mock_session.execute.return_value = mock_res2
            mastery = await repo.get_subject_mastery("l-1")
            assert len(mastery) == 1
            assert mastery[0]["subject_code"] == "MATH"

            # 3. persist_report
            report_id = await repo.persist_report("l-1", "g-1", 0.9, "Great progress", [{"subject": "MATH"}])
            assert report_id is not None
            mock_session.commit.assert_called_once()

            # 4. get_reports_for_learner
            mock_res4 = MagicMock()
            mock_res4.mappings.return_value.all.return_value = [{"report_id": "rep-1", "content": {}}]
            mock_session.execute.return_value = mock_res4
            reports = await repo.get_reports_for_learner("l-1", "g-1")
            assert len(reports) == 1
            assert reports[0]["report_id"] == "rep-1"


class TestStripeEventRepository:
    @pytest.mark.asyncio
    async def test_stripe_event_repository_methods(self):
        from app.repositories.stripe_event_repository import StripeEventRepository

        # Without bound session
        repo_unbound = StripeEventRepository()
        with pytest.raises(ValueError, match="requires a bound session"):
            await repo_unbound.is_processed("evt-1")

        with pytest.raises(ValueError, match="requires a bound session"):
            await repo_unbound.record("evt-1", "charge.succeeded", {})

        # With bound session
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_res

        repo = StripeEventRepository(db=mock_db)
        assert await repo.exists(mock_db, "evt-1") is True
        assert await repo.is_processed("evt-1") is True

        repo.create = AsyncMock(return_value=MagicMock(stripe_event_id="evt-1"))
        recorded = await repo.record("evt-1", "charge.succeeded", {"amount": 100})
        assert recorded.stripe_event_id == "evt-1"


class TestKnowledgeGapRepository:
    @pytest.mark.asyncio
    async def test_knowledge_gap_repository_methods(self):
        from app.repositories.knowledge_gap_repository import KnowledgeGapRepository
        from types import SimpleNamespace

        repo = KnowledgeGapRepository()
        mock_db = AsyncMock()
        mock_res = MagicMock()
        uid = uuid.uuid4()

        # 1. get_active_for_learner
        mock_gap = SimpleNamespace(id="gap-1", learner_id=uid, severity=0.8, resolved=False)
        mock_res.scalars.return_value.all.return_value = [mock_gap]
        mock_db.execute.return_value = mock_res

        active_gaps = await repo.get_active_for_learner(uid, mock_db)
        assert len(active_gaps) == 1
        assert active_gaps[0].severity == 0.8

        # 2. upsert_gap - existing gap updates severity
        mock_res_exist = MagicMock()
        mock_res_exist.scalar_one_or_none.return_value = mock_gap
        mock_db.execute.return_value = mock_res_exist
        mock_db.add = MagicMock()

        updated_gap = await repo.upsert_gap(mock_db, uid, 4, "MATH", "Fractions", 0.95)
        assert updated_gap.severity == 0.95
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()

        # 3. upsert_gap - non-existing creates new gap
        mock_res_none = MagicMock()
        mock_res_none.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_res_none
        new_gap = SimpleNamespace(id="gap-new", learner_id=uid, severity=0.5)
        repo.create = AsyncMock(return_value=new_gap)

        created_gap = await repo.upsert_gap(mock_db, uid, 4, "MATH", "Decimals", 0.5)
        assert created_gap.id == "gap-new"
