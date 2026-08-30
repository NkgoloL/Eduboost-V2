"""Comprehensive unit tests for ItemBankRepository."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.repositories.item_bank_repository import ItemBankRepository
from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.domain.item_schema import ReviewStatus


class TestItemBankRepository:
    def test_repo_init(self):
        mock_db = AsyncMock()
        repo = ItemBankRepository(mock_db)
        assert repo.db == mock_db

    @pytest.mark.asyncio
    async def test_get_item_found(self):
        mock_db = AsyncMock()
        mock_item = MagicMock(spec=DiagnosticItem)
        mock_item.item_id = uuid.uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        mock_db.execute.return_value = mock_result

        repo = ItemBankRepository(mock_db)
        item = await repo.get_item(mock_item.item_id)
        assert item == mock_item

    @pytest.mark.asyncio
    async def test_get_item_not_found(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        repo = ItemBankRepository(mock_db)
        item = await repo.get_item(uuid.uuid4())
        assert item is None

    @pytest.mark.asyncio
    async def test_list_by_caps_ref(self):
        mock_db = AsyncMock()
        mock_items = [MagicMock(spec=DiagnosticItem), MagicMock(spec=DiagnosticItem)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_items
        mock_db.execute.return_value = mock_result

        repo = ItemBankRepository(mock_db)
        res = await repo.list_by_caps_ref("4.M.1.1", review_status=ReviewStatus.APPROVED)
        assert len(res) == 2
