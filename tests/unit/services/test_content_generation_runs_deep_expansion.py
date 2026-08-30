"""Comprehensive unit tests for ContentGenerationRunService and task states."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.content_generation_runs import (
    TASK_STATES,
    ContentGenerationRunService,
)


class TestContentGenerationRunModels:
    def test_task_states_constant(self):
        assert "queued" in TASK_STATES
        assert "running" in TASK_STATES
        assert "succeeded" in TASK_STATES
        assert "failed" in TASK_STATES
        assert "cancelled" in TASK_STATES
        assert "skipped" in TASK_STATES

    def test_generation_run_service_init(self):
        mock_registry = MagicMock()
        service = ContentGenerationRunService(scope_registry=mock_registry)
        assert service.scope_registry == mock_registry
