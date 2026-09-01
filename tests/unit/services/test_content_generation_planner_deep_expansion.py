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


class TestContentGenerationPlannerExecution:
    @pytest.mark.asyncio
    async def test_plan_missing_for_run_not_found(self):
        from unittest.mock import AsyncMock
        mock_session = AsyncMock()
        mock_session.get.return_value = None

        planner = ContentGenerationPlanner()
        with pytest.raises(LookupError) as exc_info:
            await planner.plan_missing_for_run(mock_session, uuid.uuid4())
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_plan_missing_for_run_full_branch_flow(self):
        from unittest.mock import AsyncMock, MagicMock
        from types import SimpleNamespace
        from app.models.content_factory import ContentGenerationRun

        run_id = uuid.uuid4()
        run = ContentGenerationRun(run_id=run_id, scope_id="grade4_maths_en", status="created")

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.get.return_value = run

        mock_registry = MagicMock()
        scope = SimpleNamespace(
            scope_id="grade4_maths_en",
            grade=4,
            subject_code="MATH",
            language="en",
            topic_map=[SimpleNamespace(caps_ref="4.M.1.1", title="Numbers and Ops")],
        )
        mock_registry.get_scope.return_value = scope

        # Layers:
        # 1. Non-plannable layer (ignored)
        # 2. Target <= 0 (ignored)
        # 3. Coverage green (target=10, approved=10)
        # 4. Context failed (target=10, approved=0, passed=False)
        # 5. Duplicate task (target=10, approved=0, passed=True, existing_task!=None)
        # 6. Valid task creation (target=10, approved=0, passed=True, existing_task=None)
        mock_readiness = MagicMock()
        layers = [
            SimpleNamespace(layer="unknown_layer", target=10, approved=0, caps_ref="4.M.1.0"),
            SimpleNamespace(layer="diagnostic_items", target=0, approved=0, caps_ref="4.M.1.0"),
            SimpleNamespace(layer="diagnostic_items", target=10, approved=10, caps_ref="4.M.1.1"),
            SimpleNamespace(layer="lessons", target=10, approved=0, caps_ref="4.M.1.2"),
            SimpleNamespace(layer="assessment_blueprints", target=10, approved=0, caps_ref="4.M.1.3"),
            SimpleNamespace(layer="study_plan_templates", target=10, approved=0, caps_ref="4.M.1.4"),
        ]
        mock_report = SimpleNamespace(layers=layers)
        mock_readiness.verify_scope = AsyncMock(return_value=mock_report)

        mock_source = MagicMock()
        mock_source.build_context = AsyncMock(side_effect=[
            SimpleNamespace(passed=False, errors=["missing text"]),  # for lessons
            SimpleNamespace(passed=True, errors=[]),                 # for assessment_blueprints
            SimpleNamespace(passed=True, errors=[]),                 # for study_plan_templates
        ])

        # For existing task query:
        # First call: duplicate task (returns existing)
        # Second call: new task (returns None)
        mock_existing_task = MagicMock()
        mock_scalar_res1 = MagicMock()
        mock_scalar_res1.scalar_one_or_none.return_value = mock_existing_task
        mock_scalar_res2 = MagicMock()
        mock_scalar_res2.scalar_one_or_none.return_value = None
        mock_session.execute.side_effect = [mock_scalar_res1, mock_scalar_res2]

        planner = ContentGenerationPlanner(
            scope_registry=mock_registry,
            readiness_service=mock_readiness,
            source_context_service=mock_source,
        )

        result = await planner.plan_missing_for_run(mock_session, run_id)

        assert result.run_id == run_id
        assert len(result.created_task_ids) == 1
        assert len(result.missing) == 1
        assert run.status == "planned"
        assert mock_session.add.call_count == 1
        assert mock_session.flush.call_count == 1

        # Check skip reasons
        skip_reasons = {s["reason"] for s in result.skipped}
        assert "coverage_green" in skip_reasons
        assert "missing_source_context" in skip_reasons
        assert "duplicate_task" in skip_reasons

    def test_topic_title_fallback(self):
        from types import SimpleNamespace
        from app.services.content_generation_planner import _topic_title

        scope = SimpleNamespace(
            topic_map=[SimpleNamespace(caps_ref="4.M.1.1", title="Known Topic")]
        )
        assert _topic_title(scope, "4.M.1.1") == "Known Topic"
        assert _topic_title(scope, "UNKNOWN") == "UNKNOWN"
        assert _topic_title(None, "FALLBACK") == "FALLBACK"
