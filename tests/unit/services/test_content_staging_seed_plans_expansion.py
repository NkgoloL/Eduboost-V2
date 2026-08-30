import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.content_staging_seed_executor import (
    StagingSeedRunPage,
    StagingRollbackResult,
    ContentStagingSeedExecutor,
)


def test_staging_seed_page_and_rollback():
    run_id = uuid.uuid4()
    rollback = StagingRollbackResult(
        seed_run_id=run_id,
        status="rolled_back",
        rolled_back_count=5,
    )
    assert rollback.seed_run_id == run_id
    assert rollback.rolled_back_count == 5

    page = StagingSeedRunPage(
        items=[],
        total=0,
        limit=50,
        offset=0,
    )
    assert page.total == 0
    assert page.limit == 50


@pytest.mark.asyncio
async def test_staging_seed_dry_run():
    executor = ContentStagingSeedExecutor()
    mock_plan = MagicMock()
    mock_plan.seedable = []
    mock_plan.skipped = []
    executor._plan_seed = AsyncMock(return_value=mock_plan)

    session = AsyncMock()
    plan = await executor.dry_run_seed(session, "scope-1")
    assert plan == mock_plan
    executor._plan_seed.assert_awaited_once_with(session, "scope-1", layers=None)
