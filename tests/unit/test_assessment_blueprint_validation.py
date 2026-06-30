from app.services.content_blueprint_validation import AssessmentBlueprintValidationService


def test_blueprints_may_reference_only_approved_diagnostic_items() -> None:
    result = AssessmentBlueprintValidationService().validate({"blueprint_json": {}, "referenced_artifact_ids": ["bad"]}, {"good"})
    assert result.passed is False
    assert any("approved diagnostic" in error for error in result.errors)
