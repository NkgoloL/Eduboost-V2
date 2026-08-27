"""Comprehensive unit tests for Repository layer: ItemBankRepository, RuntimeKGRepository, AuditRepository, and LessonRepository."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.audit_repository import (
    AuditRepository,
    compute_audit_hash,
    configure_hmac_secret,
)
from app.repositories.lesson_repository import LessonRepository
from app.services.runtime_kg.repository import RuntimeKGRepository
from app.models.diagnostic_item import DiagnosticItem


# ---------------------------------------------------------------------------
# Audit Repository & Hash Tests
# ---------------------------------------------------------------------------

class TestAuditRepository:
    def test_compute_audit_hash(self):
        eid = uuid.uuid4()
        h = compute_audit_hash(
            event_id=eid,
            event_type="consent_granted",
            actor_id="parent_1",
            resource_id="learner_1",
            previous_event_hash="prev_hash_123",
            payload={"scope": "all"},
        )
        assert isinstance(h, str)
        assert len(h) == 64

    def test_configure_hmac_secret(self):
        configure_hmac_secret(b"test_secret_12345")


# ---------------------------------------------------------------------------
# Item Bank Repository Tests
# ---------------------------------------------------------------------------

class TestItemBankRepository:
    def test_item_bank_repo_init(self):
        mock_db = AsyncMock()
        repo = ItemBankRepository(db=mock_db)
        assert repo.db == mock_db

    @pytest.mark.asyncio
    async def test_get_item_found(self):
        mock_db = AsyncMock()
        item_id = uuid.uuid4()
        fake_item = MagicMock(spec=DiagnosticItem)
        fake_item.item_id = item_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = fake_item
        mock_db.execute.return_value = mock_result

        repo = ItemBankRepository(db=mock_db)
        item = await repo.get_item(item_id)
        assert item == fake_item
        mock_db.execute.assert_called_once()


# ---------------------------------------------------------------------------
# Lesson Repository Tests
# ---------------------------------------------------------------------------

class TestLessonRepository:
    def test_lesson_repo_init(self):
        mock_db = AsyncMock()
        repo = LessonRepository(db=mock_db)
        assert repo.db == mock_db

    def test_lesson_repo_requires_session_if_none(self):
        repo = LessonRepository(db=None)
        with pytest.raises(RuntimeError, match="LessonRepository requires an AsyncSession"):
            repo._db()


# ---------------------------------------------------------------------------
# Runtime KG Repository Tests
# ---------------------------------------------------------------------------

class TestRuntimeKGRepository:
    def test_runtime_kg_repo_init(self):
        mock_db = AsyncMock()
        repo = RuntimeKGRepository(db=mock_db)
        assert repo.db == mock_db
        assert repo.loader is not None
