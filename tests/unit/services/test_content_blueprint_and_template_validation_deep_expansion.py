"""Comprehensive unit tests for assessment blueprint and study plan template validation."""
from __future__ import annotations

import pytest

from app.services.content_blueprint_validation import (
    BlueprintValidationResult,
    AssessmentBlueprintValidationService,
)
from app.services.content_template_validation import (
    StudyPlanTemplateValidationResult,
    StudyPlanTemplateValidationService,
)


class TestAssessmentBlueprintValidation:
    def test_blueprint_validation_result_dataclass(self):
        res = BlueprintValidationResult(passed=True, errors=[])
        assert res.passed is True
        assert len(res.errors) == 0

    def test_blueprint_validate_success(self):
        service = AssessmentBlueprintValidationService()
        blueprint = {
            "blueprint_json": {"topics": ["fractions"]},
            "referenced_artifact_ids": ["art_1", "art_2"],
        }
        res = service.validate(blueprint, approved_diagnostic_item_ids={"art_1", "art_2", "art_3"})
        assert res.passed is True
        assert len(res.errors) == 0

    def test_blueprint_validate_missing_json(self):
        service = AssessmentBlueprintValidationService()
        blueprint = {"referenced_artifact_ids": ["art_1"]}
        res = service.validate(blueprint, approved_diagnostic_item_ids={"art_1"})
        assert res.passed is False
        assert any("requires content_json or blueprint_json" in err for err in res.errors)

    def test_blueprint_validate_unapproved_references(self):
        service = AssessmentBlueprintValidationService()
        blueprint = {
            "content_json": {"name": "Assessment 1"},
            "referenced_artifact_ids": ["art_unapproved"],
        }
        res = service.validate(blueprint, approved_diagnostic_item_ids={"art_1"})
        assert res.passed is False
        assert any("reference only approved diagnostic items" in err for err in res.errors)


class TestStudyPlanTemplateValidation:
    def test_study_plan_template_validation_result_dataclass(self):
        res = StudyPlanTemplateValidationResult(passed=True, errors=[])
        assert res.passed is True
        assert len(res.errors) == 0

    def test_template_validate_success(self):
        service = StudyPlanTemplateValidationService()
        template = {
            "template_json": {"steps": [1, 2, 3]},
            "referenced_artifact_ids": ["les_1", "bp_1"],
        }
        res = service.validate(template, approved_reference_ids={"les_1", "bp_1", "les_2"})
        assert res.passed is True
        assert len(res.errors) == 0

    def test_template_validate_missing_json(self):
        service = StudyPlanTemplateValidationService()
        template = {"referenced_artifact_ids": ["les_1"]}
        res = service.validate(template, approved_reference_ids={"les_1"})
        assert res.passed is False
        assert any("requires content_json or template_json" in err for err in res.errors)

    def test_template_validate_unapproved_references(self):
        service = StudyPlanTemplateValidationService()
        template = {
            "content_json": {"name": "Plan 1"},
            "referenced_artifact_ids": ["unapproved_les"],
        }
        res = service.validate(template, approved_reference_ids={"les_1"})
        assert res.passed is False
        assert any("reference only approved lessons or blueprints" in err for err in res.errors)
