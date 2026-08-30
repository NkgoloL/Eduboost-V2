"""Comprehensive unit tests for grounded batch generation engine and task specs."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.content_factory import ContentLayer
from app.services.batch_generation import (
    GenerationTaskSpec,
    RunResult,
    _LOCK_DURATION,
    _acquire_task_lock,
    BatchGenerationEngine,
)


class TestBatchGenerationSpecsAndResults:
    def test_generation_task_spec_defaults(self):
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
        assert res.succeeded == 8
        assert res.failed == 1
        assert res.safety_blocked == 1

    def test_lock_duration(self):
        assert _LOCK_DURATION.total_seconds() == 600

    @pytest.mark.asyncio
    async def test_acquire_task_lock_acquired(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = uuid.uuid4()
        mock_db.execute.return_value = mock_result

        tid = uuid.uuid4()
        acquired = await _acquire_task_lock(tid, "worker_1", mock_db)
        assert acquired is True
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_acquire_task_lock_rejected(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        tid = uuid.uuid4()
        acquired = await _acquire_task_lock(tid, "worker_1", mock_db)
        assert acquired is False


class TestBatchGenerationEngine:
    def test_engine_init(self):
        mock_router = MagicMock()
        mock_registry = MagicMock()
        mock_validator = MagicMock()
        mock_safety = MagicMock()
        mock_provenance = MagicMock()

        engine = BatchGenerationEngine(
            provider_router=mock_router,
            prompt_registry=mock_registry,
            validator=mock_validator,
            safety_filter=mock_safety,
            provenance_service=mock_provenance,
        )
        assert engine._router == mock_router
        assert engine._registry == mock_registry
        assert engine._validator == mock_validator
        assert engine._safety == mock_safety
        assert engine._provenance == mock_provenance
