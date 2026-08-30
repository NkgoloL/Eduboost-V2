"""Comprehensive unit tests for ContentGenerationPlanner models and initialization."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
import pytest

from app.services.content_generation_planner import (
    PLANNABLE_LAYERS,
    DEFAULT_PROMPT_VERSION,
    DEFAULT_TARGET_VERSION,
    DEFAULT_GENERATOR_VERSION,
    GenerationPlanResult,
    ContentGenerationPlanner,
)


class TestContentGenerationPlannerModels:
    def test_plannable_layers_constants(self):
        assert "diagnostic_items" in PLANNABLE_LAYERS
        assert "lessons" in PLANNABLE_LAYERS
        assert "assessment_blueprints" in PLANNABLE_LAYERS
        assert "study_plan_templates" in PLANNABLE_LAYERS

    def test_version_constants(self):
        assert DEFAULT_PROMPT_VERSION == "cf-gen-v1"
        assert DEFAULT_TARGET_VERSION == "1.0"
        assert DEFAULT_GENERATOR_VERSION == "1.0"

    def test_generation_plan_result_dataclass(self):
        rid = uuid.uuid4()
        tid = uuid.uuid4()
        res = GenerationPlanResult(
            run_id=rid,
            created_task_ids=[tid],
            skipped=[],
            missing=[],
        )
        assert res.run_id == rid
        assert len(res.created_task_ids) == 1

    def test_generation_planner_init(self):
        mock_registry = MagicMock()
        mock_readiness = MagicMock()
        mock_source = MagicMock()

        planner = ContentGenerationPlanner(
            scope_registry=mock_registry,
            readiness_service=mock_readiness,
            source_context_service=mock_source,
        )
        assert planner.scope_registry == mock_registry
        assert planner.readiness_service == mock_readiness
        assert planner.source_context_service == mock_source
