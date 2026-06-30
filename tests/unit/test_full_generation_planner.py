"""Unit tests for full generation planner."""
from __future__ import annotations


import pytest

from app.domain.content_coverage import ContentLayer
from app.services.content_generation_planner import (
    ContentGenerationPlanner,
    DEFAULT_GENERATOR_VERSION,
    DEFAULT_PROMPT_VERSION,
    DEFAULT_TARGET_VERSION,
    PLANNABLE_LAYERS,
)


@pytest.mark.unit
def test_planner_instantiation() -> None:
    """Planner can be instantiated."""
    planner = ContentGenerationPlanner()
    assert planner is not None
    assert planner.scope_registry is not None
    assert planner.readiness_service is not None
    assert planner.source_context_service is not None


@pytest.mark.unit
def test_plannable_layers_includes_all_layers() -> None:
    """Plannable layers includes all required content layers."""
    assert ContentLayer.DIAGNOSTIC_ITEMS.value in PLANNABLE_LAYERS
    assert ContentLayer.LESSONS.value in PLANNABLE_LAYERS
    assert ContentLayer.ASSESSMENT_BLUEPRINTS.value in PLANNABLE_LAYERS
    assert ContentLayer.STUDY_PLAN_TEMPLATES.value in PLANNABLE_LAYERS


@pytest.mark.unit
def test_default_versions_are_set() -> None:
    """Default versions are configured."""
    assert DEFAULT_PROMPT_VERSION == "cf-gen-v1"
    assert DEFAULT_TARGET_VERSION == "1.0"
    assert DEFAULT_GENERATOR_VERSION == "1.0"


@pytest.mark.unit
def test_planner_has_plan_missing_for_run_method() -> None:
    """Planner has plan_missing_for_run method."""
    planner = ContentGenerationPlanner()
    assert hasattr(planner, "plan_missing_for_run")
    assert callable(getattr(planner, "plan_missing_for_run"))


@pytest.mark.unit
def test_planner_accepts_generator_version_parameter() -> None:
    """Planner accepts generator_version parameter."""
    planner = ContentGenerationPlanner()
    import inspect
    sig = inspect.signature(planner.plan_missing_for_run)
    assert "generator_version" in sig.parameters
    assert sig.parameters["generator_version"].default == DEFAULT_GENERATOR_VERSION
