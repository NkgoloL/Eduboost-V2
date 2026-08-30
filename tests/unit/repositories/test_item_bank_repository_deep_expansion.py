import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.repositories.item_bank_repository import ItemBankRepository


@pytest.mark.asyncio
async def test_item_bank_repo_get_item():
    db = AsyncMock()
    repo = ItemBankRepository(db)

    item_id = uuid.uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    item = await repo.get_item(item_id)
    assert item is None
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_item_bank_repo_list_by_caps_ref():
    db = AsyncMock()
    repo = ItemBankRepository(db)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    items = await repo.list_by_caps_ref("4.M.1.1", review_status=ReviewStatusEnum.APPROVED)
    assert items == []
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_item_bank_repo_get_unexposed_items():
    db = AsyncMock()
    repo = ItemBankRepository(db)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    learner_id = uuid.uuid4()
    items = await repo.get_unexposed_items(learner_id, "4.M.1.1", min_b_param=-1.0, max_b_param=1.0)
    assert items == []
    db.execute.assert_awaited_once()
