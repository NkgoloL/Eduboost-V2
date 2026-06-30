"""Study-plan template validation skeleton."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudyPlanTemplateValidationResult:
    passed: bool
    errors: list[str]


class StudyPlanTemplateValidationService:
    def validate(self, template: dict, approved_reference_ids: set[str]) -> StudyPlanTemplateValidationResult:
        errors: list[str] = []
        referenced = {str(item) for item in template.get("referenced_artifact_ids", [])}
        if not template.get("content_json") and not template.get("template_json"):
            errors.append("Study plan template requires content_json or template_json.")
        missing = referenced - approved_reference_ids
        if missing:
            errors.append("Study templates may reference only approved lessons or blueprints: " + ", ".join(sorted(missing)))
        return StudyPlanTemplateValidationResult(not errors, errors)
