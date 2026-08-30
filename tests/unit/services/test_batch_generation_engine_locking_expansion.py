"""Comprehensive unit tests for BatchGenerationEngine task specification and concurrency locking."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.content_factory import ContentLayer
from app.services.batch_generation import (
    GenerationTaskSpec,
    RunResult,
    _acquire_task_lock,
    BatchGenerationEngine,
)


class TestBatchGenerationDataclassesAndLocking:
    def test_generation_task_spec_defaults(self):
        spec = GenerationTaskSpec(
            caps_ref="4.M.1.1",
            content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
            content_type="diagnostic_item",
        )
        assert spec.caps_ref == "4.M.1.1"
        assert spec.content_layer == ContentLayer.DIAGNOSTIC_ITEMS
        assert spec.count == 5
        assert spec.language == "en"
        assert spec.grade == 4
        assert spec.subject == "Mathematics"
        assert spec.subject_code == "MATHS"

    def test_run_result_dataclass(self):
        rid = uuid.uuid4()
        res = RunResult(
            run_id=rid,
            total_tasks=10,
            succeeded=8,
            failed=1,
            safety_blocked=1,
            skipped=0,
        )
        assert res.run_id == rid
        assert res.total_tasks == 10
        assert res.succeeded == 8

    @pytest.mark.asyncio
    async def test_acquire_task_lock_success(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        tid = uuid.uuid4()
        mock_res.scalar_one_or_none.return_value = tid
        mock_db.execute.return_value = mock_res

        acquired = await _acquire_task_lock(
            task_id=tid,
            worker_id="worker_test_1",
            db=mock_db,
        )
        assert acquired is True
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_acquire_task_lock_already_locked(self):
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_res

        acquired = await _acquire_task_lock(
            task_id=uuid.uuid4(),
            worker_id="worker_test_2",
            db=mock_db,
        )
        assert acquired is False

    def test_batch_generation_engine_init(self):
        mock_router = MagicMock()
        mock_registry = MagicMock()
        mock_safety = MagicMock()
        mock_validator = MagicMock()
        mock_provenance = MagicMock()
        mock_source_ctx = MagicMock()

        engine = BatchGenerationEngine(
            provider_router=mock_router,
            prompt_registry=mock_registry,
            safety_filter=mock_safety,
            validator=mock_validator,
            provenance_service=mock_provenance,
            source_context_service=mock_source_ctx,
        )
        assert engine._router == mock_router
        assert engine._registry == mock_registry
        assert engine._safety == mock_safety
        assert engine._validator == mock_validator
        assert engine._provenance == mock_provenance
        assert engine._source_context == mock_source_ctx
