"""Assessment blueprint validation skeleton."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlueprintValidationResult:
    passed: bool
    errors: list[str]


class AssessmentBlueprintValidationService:
    def validate(self, blueprint: dict, approved_diagnostic_item_ids: set[str]) -> BlueprintValidationResult:
        errors: list[str] = []
        referenced = {str(item) for item in blueprint.get("referenced_artifact_ids", [])}
        if not blueprint.get("content_json") and not blueprint.get("blueprint_json"):
            errors.append("Blueprint requires content_json or blueprint_json.")
        missing = referenced - approved_diagnostic_item_ids
        if missing:
            errors.append("Blueprint may reference only approved diagnostic items: " + ", ".join(sorted(missing)))
        return BlueprintValidationResult(not errors, errors)
