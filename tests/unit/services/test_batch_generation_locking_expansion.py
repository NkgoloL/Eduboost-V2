import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.batch_generation import (
    GenerationTaskSpec,
    RunResult,
    _acquire_task_lock,
    BatchGenerationEngine,
)
from app.models.content_factory import ContentLayer


def test_generation_task_spec_defaults():
    spec = GenerationTaskSpec(
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.LESSONS,
        content_type="lesson",
    )
    assert spec.count == 5
    assert spec.language == "en"
    assert spec.grade == 4
    assert spec.subject == "Mathematics"

    res = RunResult(
        run_id=uuid.uuid4(),
        total_tasks=10,
        succeeded=8,
        failed=1,
        safety_blocked=1,
        skipped=0,
    )
    assert res.total_tasks == 10
    assert res.succeeded == 8


@pytest.mark.asyncio
async def test_acquire_task_lock():
    db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = uuid.uuid4()
    db.execute.return_value = mock_res

    acquired = await _acquire_task_lock(uuid.uuid4(), "worker-1", db)
    assert acquired is True
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_run_empty_tasks_raises():
    router = MagicMock()
    engine = BatchGenerationEngine(provider_router=router)
    db = AsyncMock()

    with pytest.raises(ValueError, match="At least one generation task is required"):
        await engine.create_run(
            scope_id="scope-1",
            task_specs=[],
            sources_by_caps_ref={},
            requested_by="admin",
            db=db,
        )
