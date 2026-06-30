"""Unit tests for study-plan template generator."""
from __future__ import annotations


import pytest

from app.services.content_generation.study_plan_template_generator import StudyPlanTemplateGenerator


@pytest.mark.unit
def test_study_plan_template_generator_instantiation() -> None:
    """StudyPlanTemplateGenerator can be instantiated."""
    generator = StudyPlanTemplateGenerator()
    assert generator is not None


@pytest.mark.unit
def test_study_plan_template_generator_has_generate_method() -> None:
    """StudyPlanTemplateGenerator has generate method."""
    generator = StudyPlanTemplateGenerator()
    assert hasattr(generator, "generate")
    assert callable(getattr(generator, "generate"))


@pytest.mark.unit
def test_study_plan_template_generator_returns_schema_valid_artifact() -> None:
    """StudyPlanTemplateGenerator returns schema-valid artifact."""
    generator = StudyPlanTemplateGenerator()
    # Test the deterministic generation directly
    payload = generator._generate_deterministic_template(
        scope_id="test_scope",
        caps_ref="8.1.1",
        grade=8,
        subject_code="MAT",
        language="en",
    )
    assert payload["scope_id"] == "test_scope"
    assert payload["caps_ref"] == "8.1.1"
    assert payload["grade"] == 8
    assert payload["subject_code"] == "MAT"
    assert payload["language"] == "en"
    assert "diagnostic_trigger_conditions" in payload
    assert "estimated_minutes" in payload


@pytest.mark.unit
def test_study_plan_template_generator_validates_payload() -> None:
    """StudyPlanTemplateGenerator validates payload."""
    generator = StudyPlanTemplateGenerator()
    payload = generator._generate_deterministic_template(
        scope_id="test_scope",
        caps_ref="8.1.1",
        grade=8,
        subject_code="MAT",
        language="en",
    )
    errors = generator._validate_template(payload, "test_scope", "8.1.1")
    assert len(errors) == 0


@pytest.mark.unit
def test_study_plan_template_generator_detects_missing_caps_ref() -> None:
    """StudyPlanTemplateGenerator detects missing caps_ref."""
    generator = StudyPlanTemplateGenerator()
    payload = generator._generate_deterministic_template(
        scope_id="test_scope",
        caps_ref="8.1.1",
        grade=8,
        subject_code="MAT",
        language="en",
    )
    payload["caps_ref"] = None
    errors = generator._validate_template(payload, "test_scope", "8.1.1")
    assert len(errors) > 0
    assert any("caps_ref" in error for error in errors)


@pytest.mark.unit
def test_study_plan_template_generator_detects_caps_ref_mismatch() -> None:
    """StudyPlanTemplateGenerator detects caps_ref mismatch."""
    generator = StudyPlanTemplateGenerator()
    payload = generator._generate_deterministic_template(
        scope_id="test_scope",
        caps_ref="8.1.1",
        grade=8,
        subject_code="MAT",
        language="en",
    )
    errors = generator._validate_template(payload, "test_scope", "8.1.2")
    assert len(errors) > 0
    assert any("mismatch" in error for error in errors)
