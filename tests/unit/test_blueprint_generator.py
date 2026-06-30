"""Unit tests for blueprint generator."""
from __future__ import annotations


import pytest

from app.services.content_generation.blueprint_generator import BlueprintGenerator


@pytest.mark.unit
def test_blueprint_generator_instantiation() -> None:
    """BlueprintGenerator can be instantiated."""
    generator = BlueprintGenerator()
    assert generator is not None


@pytest.mark.unit
def test_blueprint_generator_has_generate_method() -> None:
    """BlueprintGenerator has generate method."""
    generator = BlueprintGenerator()
    assert hasattr(generator, "generate")
    assert callable(getattr(generator, "generate"))


@pytest.mark.unit
def test_blueprint_generator_returns_schema_valid_artifact() -> None:
    """BlueprintGenerator returns schema-valid artifact."""
    generator = BlueprintGenerator()
    # Test the deterministic generation directly
    payload = generator._generate_deterministic_blueprint(
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
    assert "assessment_type" in payload
    assert "question_mix" in payload


@pytest.mark.unit
def test_blueprint_generator_validates_payload() -> None:
    """BlueprintGenerator validates payload."""
    generator = BlueprintGenerator()
    payload = generator._generate_deterministic_blueprint(
        scope_id="test_scope",
        caps_ref="8.1.1",
        grade=8,
        subject_code="MAT",
        language="en",
    )
    errors = generator._validate_blueprint(payload, "test_scope", "8.1.1")
    assert len(errors) == 0


@pytest.mark.unit
def test_blueprint_generator_detects_missing_caps_ref() -> None:
    """BlueprintGenerator detects missing caps_ref."""
    generator = BlueprintGenerator()
    payload = generator._generate_deterministic_blueprint(
        scope_id="test_scope",
        caps_ref="8.1.1",
        grade=8,
        subject_code="MAT",
        language="en",
    )
    payload["caps_ref"] = None
    errors = generator._validate_blueprint(payload, "test_scope", "8.1.1")
    assert len(errors) > 0
    assert any("caps_ref" in error for error in errors)


@pytest.mark.unit
def test_blueprint_generator_detects_caps_ref_mismatch() -> None:
    """BlueprintGenerator detects caps_ref mismatch."""
    generator = BlueprintGenerator()
    payload = generator._generate_deterministic_blueprint(
        scope_id="test_scope",
        caps_ref="8.1.1",
        grade=8,
        subject_code="MAT",
        language="en",
    )
    errors = generator._validate_blueprint(payload, "test_scope", "8.1.2")
    assert len(errors) > 0
    assert any("mismatch" in error for error in errors)
