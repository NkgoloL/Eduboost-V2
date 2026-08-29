import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.content_review_governance import (
    ContentReviewGovernanceService,
)


@pytest.mark.asyncio
async def test_list_history():
    service = ContentReviewGovernanceService()
    session = AsyncMock()

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    session.scalars.return_value = mock_scalars

    hist = await service.list_history(session, uuid.uuid4())
    assert "decisions" in hist
    assert "transitions" in hist
    assert hist["decisions"] == []
    assert hist["transitions"] == []


@pytest.mark.asyncio
async def test_process_stale_assignments_empty():
    service = ContentReviewGovernanceService()
    session = AsyncMock()

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    session.scalars.return_value = mock_scalars

    res = await service.process_stale_assignments(session)
    assert res["stale"] == 0
    assert res["reminded"] == 0
    assert res["escalated"] == 0
