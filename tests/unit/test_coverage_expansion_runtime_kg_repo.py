"""
Unit tests for app.services.runtime_kg.repository to expand coverage.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.runtime_kg.repository import RuntimeKGRepository


@pytest.mark.asyncio
async def test_get_active_graph():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_load = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_load
    db.execute.return_value = mock_result

    repo = RuntimeKGRepository(db)
    active = await repo.get_active_graph(graph_version="v1.0")

    assert active == mock_load
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_load_graph_idempotent_existing():
    db = AsyncMock()
    mock_result = MagicMock()
    existing_load = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_load
    db.execute.return_value = mock_result

    from app.services.runtime_kg.schemas import RuntimeKGGraphInput, RuntimeKGNodeInput
    node = RuntimeKGNodeInput(
        stable_code="NODE-01",
        node_type="concept",
        label="Test Node",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATH",
    )
    graph_input = RuntimeKGGraphInput(
        graph_version="v1.0",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATH",
        source_ref="ref",
        source_sha256="a" * 64,
        loaded_by="tester",
        nodes=(node,),
        edges=(),
    )

    repo = RuntimeKGRepository(db)
    res = await repo.load_graph_idempotent(graph_input)

    assert res == existing_load
