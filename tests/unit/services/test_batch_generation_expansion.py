import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.content_factory import ContentLayer
from app.services.batch_generation import (
    BatchGenerationEngine,
    GenerationTaskSpec,
    RunResult,
    _acquire_task_lock,
)


def test_generation_task_spec_defaults():
    spec = GenerationTaskSpec(
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        content_type="diagnostic_item",
    )
    assert spec.count == 5
    assert spec.language == "en"
    assert spec.grade == 4
    assert spec.subject == "Mathematics"
    assert spec.subject_code == "MATHS"


def test_run_result_dataclass():
    run_id = uuid.uuid4()
    res = RunResult(
        run_id=run_id,
        total_tasks=10,
        succeeded=8,
        failed=1,
        safety_blocked=1,
        skipped=0,
    )
    assert res.run_id == run_id
    assert res.total_tasks == 10
    assert res.succeeded == 8


@pytest.mark.asyncio
async def test_create_run_validation():
    mock_router = MagicMock()
    engine = BatchGenerationEngine(provider_router=mock_router)
    db = AsyncMock()

    # Empty task specs
    with pytest.raises(ValueError, match="At least one generation task is required"):
        await engine.create_run(
            scope_id="scope1",
            task_specs=[],
            sources_by_caps_ref={},
            requested_by="admin",
            db=db,
        )


@pytest.mark.asyncio
async def test_create_run_provenance_failure():
    mock_router = MagicMock()
    mock_prov = MagicMock()
    gate_mock = MagicMock()
    gate_mock.passed = False
    gate_mock.errors = ["Missing verified sources"]
    mock_prov.validate_source_bundle.return_value = gate_mock

    engine = BatchGenerationEngine(
        provider_router=mock_router,
        provenance_service=mock_prov,
    )
    db = AsyncMock()

    spec = GenerationTaskSpec(
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        content_type="diagnostic_item",
    )

    with pytest.raises(ValueError, match="Source provenance failed for 4.M.1.1: Missing verified sources"):
        await engine.create_run(
            scope_id="scope1",
            task_specs=[spec],
            sources_by_caps_ref={"4.M.1.1": []},
            requested_by="admin",
            db=db,
        )


@pytest.mark.asyncio
async def test_create_run_success():
    mock_router = MagicMock()
    mock_prov = MagicMock()
    gate_mock = MagicMock()
    gate_mock.passed = True
    gate_mock.source_snapshot_hash = "fake-hash-123"
    mock_prov.validate_source_bundle.return_value = gate_mock

    engine = BatchGenerationEngine(
        provider_router=mock_router,
        provenance_service=mock_prov,
    )
    db = AsyncMock()

    spec = GenerationTaskSpec(
        caps_ref="4.M.1.1",
        content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
        content_type="diagnostic_item",
    )

    sources = [{"source_chunk_id": uuid.uuid4()}]
    run = await engine.create_run(
        scope_id="scope1",
        task_specs=[spec],
        sources_by_caps_ref={"4.M.1.1": sources},
        requested_by="admin",
        db=db,
    )

    assert run.scope_id == "scope1"
    assert run.requested_by == "admin"
    assert run.status == "created"
    assert db.add.call_count >= 2
    assert db.commit.awaited
