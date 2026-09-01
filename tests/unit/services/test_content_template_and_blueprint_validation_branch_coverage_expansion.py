"""Batch 244 — StudyPlanTemplateValidationService & AssessmentBlueprintValidationService branch coverage expansion.

Tests:
- app/services/content_template_validation.py:
  - Missing content_json / template_json
  - Referenced unapproved artifacts
  - Valid study plan template
- app/services/content_blueprint_validation.py:
  - Missing content_json / blueprint_json
  - Referenced unapproved diagnostic items
  - Valid assessment blueprint
"""
from __future__ import annotations

import pytest

from app.services.content_blueprint_validation import (
    AssessmentBlueprintValidationService,
    BlueprintValidationResult,
)
from app.services.content_template_validation import (
    StudyPlanTemplateValidationResult,
    StudyPlanTemplateValidationService,
)


# ---------------------------------------------------------------------------
# StudyPlanTemplateValidationService Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_study_plan_template_validation_service():
    svc = StudyPlanTemplateValidationService()

    # 1. Missing json content & missing referenced ID
    res_bad = svc.validate(
        template={"referenced_artifact_ids": ["art-1", "art-2"]},
        approved_reference_ids={"art-1"},
    )
    assert res_bad.passed is False
    assert any("requires content_json or template_json" in e for e in res_bad.errors)
    assert any("art-2" in e for e in res_bad.errors)

    # 2. Valid with content_json
    res_good_content = svc.validate(
        template={"content_json": {"topics": []}, "referenced_artifact_ids": ["art-1"]},
        approved_reference_ids={"art-1", "art-2"},
    )
    assert res_good_content.passed is True
    assert res_good_content.errors == []

    # 3. Valid with template_json
    res_good_template = svc.validate(
        template={"template_json": {"topics": []}, "referenced_artifact_ids": []},
        approved_reference_ids=set(),
    )
    assert res_good_template.passed is True
    assert res_good_template.errors == []


# ---------------------------------------------------------------------------
# AssessmentBlueprintValidationService Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_assessment_blueprint_validation_service():
    svc = AssessmentBlueprintValidationService()

    # 1. Missing json content & missing referenced ID
    res_bad = svc.validate(
        blueprint={"referenced_artifact_ids": ["item-100", "item-200"]},
        approved_diagnostic_item_ids={"item-100"},
    )
    assert res_bad.passed is False
    assert any("requires content_json or blueprint_json" in e for e in res_bad.errors)
    assert any("item-200" in e for e in res_bad.errors)

    # 2. Valid with content_json
    res_good_content = svc.validate(
        blueprint={"content_json": {"items": []}, "referenced_artifact_ids": ["item-100"]},
        approved_diagnostic_item_ids={"item-100"},
    )
    assert res_good_content.passed is True
    assert res_good_content.errors == []

    # 3. Valid with blueprint_json
    res_good_bp = svc.validate(
        blueprint={"blueprint_json": {"items": []}, "referenced_artifact_ids": []},
        approved_diagnostic_item_ids=set(),
    )
    assert res_good_bp.passed is True
    assert res_good_bp.errors == []
