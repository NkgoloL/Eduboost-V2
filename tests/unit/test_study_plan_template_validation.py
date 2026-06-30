from app.services.content_template_validation import StudyPlanTemplateValidationService


def test_study_templates_may_reference_only_approved_lessons_or_blueprints() -> None:
    result = StudyPlanTemplateValidationService().validate({"template_json": {}, "referenced_artifact_ids": ["bad"]}, {"good"})
    assert result.passed is False
    assert any("approved lessons or blueprints" in error for error in result.errors)
