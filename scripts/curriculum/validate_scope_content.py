#!/usr/bin/env python3
"""Validate Content Factory study material artifacts for one or more scopes."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_coverage import ContentLayer
from app.domain.content_scope import ContentScope, ContentScopeStatus
from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.modules.lessons.lesson_validator import LessonValidator
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_source_manifest import generation_ready, validate_source_manifest


@dataclass
class ScopeValidationResult:
    scope_id: str
    status: str
    skipped: bool = False
    errors: list[str] = field(default_factory=list)
    item_counts: dict[str, int] = field(default_factory=dict)
    lesson_counts: dict[str, int] = field(default_factory=dict)
    blueprint_counts: dict[str, int] = field(default_factory=dict)
    study_plan_counts: dict[str, int] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.errors


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_artifact_path(scope: ContentScope, layer: ContentLayer) -> Path:
    configured = scope.artifact_paths.get(layer.value)
    if configured:
        return ROOT / configured
    raise LookupError(f"Scope {scope.scope_id} does not declare artifact path for {layer.value}.")


def validate_scope(scope_id: str, *, strict: bool = False, registry: ContentScopeRegistry | None = None) -> ScopeValidationResult:
    registry = registry or ContentScopeRegistry()
    scope = registry.get_scope(scope_id)
    result = ScopeValidationResult(scope_id=scope.scope_id, status=scope.status.value)

    source_result = validate_source_manifest(registry=registry)
    source_errors = [error for error in source_result.errors if f"scope {scope.scope_id} " in error]
    result.errors.extend(source_errors)

    if scope.status != ContentScopeStatus.ACTIVE:
        generation_statuses = {ContentScopeStatus.GENERATING, ContentScopeStatus.REVIEW}
        if scope.status in generation_statuses:
            if not scope.topic_map_path:
                result.errors.append(f"generation scope {scope.scope_id} must declare topic_map_path")
            if not scope.caps_refs:
                result.errors.append(f"generation scope {scope.scope_id} must declare caps_refs")
            if not generation_ready(scope.scope_id, registry=registry):
                result.errors.append(f"generation scope {scope.scope_id} is not generation-ready")
        else:
            if scope.caps_refs:
                result.errors.append(f"non-generation scope {scope.scope_id} must not declare caps_refs")
            if registry.get_scope_targets(scope.scope_id):
                result.errors.append(f"non-generation scope {scope.scope_id} must not declare coverage targets")
            if generation_ready(scope.scope_id, registry=registry):
                result.errors.append(f"non-generation scope {scope.scope_id} must not be generation-ready")
        result.skipped = True
        return result

    if not generation_ready(scope.scope_id, registry=registry):
        result.errors.append(f"active scope {scope.scope_id} is not generation-ready from approved source manifest")

    if not scope.caps_refs:
        result.errors.append(f"active scope {scope.scope_id} has no caps_refs")
        return result

    topic_map_path = ROOT / str(scope.topic_map_path)
    try:
        topic_map = load_json(topic_map_path)
    except FileNotFoundError as exc:
        result.errors.append(str(exc))
        return result

    try:
        items_payload = load_json(resolve_artifact_path(scope, ContentLayer.DIAGNOSTIC_ITEMS))
        lessons_payload = load_json(resolve_artifact_path(scope, ContentLayer.LESSONS))
        blueprints_payload = load_json(resolve_artifact_path(scope, ContentLayer.ASSESSMENT_BLUEPRINTS))
        templates_payload = load_json(resolve_artifact_path(scope, ContentLayer.STUDY_PLAN_TEMPLATES))
    except (FileNotFoundError, LookupError) as exc:
        result.errors.append(str(exc))
        return result

    scope_refs = set(scope.caps_refs)
    item_validator = ItemValidator(topic_map=topic_map)
    item_counts: Counter[str] = Counter()
    for item in items_payload.get("items", []):
        caps_ref = item.get("caps_ref")
        if caps_ref not in scope_refs:
            continue
        item_errors = item_validator.validate_all(item)
        if item_errors:
            result.errors.append(f"item {item.get('item_id')} failed: {[error.rule for error in item_errors]}")
        if item.get("review_status") == "approved":
            item_counts[caps_ref] += 1

    caps_service = CAPSTopicMapService(map_paths=[topic_map_path])
    lesson_validator = LessonValidator(caps_service=caps_service)
    lesson_counts: Counter[str] = Counter()
    for lesson in lessons_payload.get("lessons", []):
        caps_ref = lesson.get("caps_ref")
        if caps_ref not in scope_refs:
            result.errors.append(f"lesson {lesson.get('lesson_id')} has out-of-scope ref {caps_ref}")
            continue
        validation = lesson_validator.validate(lesson, require_verified=True)
        if not validation.passed:
            result.errors.append(f"lesson {lesson.get('lesson_id')} failed: {validation.failures}")
        if lesson.get("review_status") == "approved":
            lesson_counts[caps_ref] += 1

    blueprint_counts: Counter[str] = Counter()
    for blueprint in blueprints_payload.get("blueprints", []):
        refs = set(blueprint.get("selection_rules", {}).get("caps_refs", []))
        if not refs or not refs <= scope_refs:
            result.errors.append(f"blueprint {blueprint.get('blueprint_id')} refs invalid: {sorted(refs)}")
            continue
        if _is_approved_blueprint(blueprint):
            for caps_ref in refs:
                blueprint_counts[caps_ref] += 1

    study_plan_counts = _study_plan_counts(templates_payload, scope_refs)

    result.item_counts = dict(item_counts)
    result.lesson_counts = dict(lesson_counts)
    result.blueprint_counts = dict(blueprint_counts)
    result.study_plan_counts = dict(study_plan_counts)

    template_refs = {row.get("caps_ref") for row in templates_payload.get("topic_sequence", [])}
    missing_template_refs = sorted(scope_refs - template_refs)
    if missing_template_refs:
        result.errors.append(f"study template missing refs: {missing_template_refs}")

    if strict:
        targets = registry.get_scope_targets(scope.scope_id)
        by_ref = {target.caps_ref: target.targets for target in targets}
        for caps_ref in scope.caps_refs:
            target = by_ref.get(caps_ref, {})
            _check_target(result, caps_ref, ContentLayer.DIAGNOSTIC_ITEMS, item_counts[caps_ref], target)
            _check_target(result, caps_ref, ContentLayer.LESSONS, lesson_counts[caps_ref], target)
            _check_target(result, caps_ref, ContentLayer.ASSESSMENT_BLUEPRINTS, blueprint_counts[caps_ref], target)
            _check_target(result, caps_ref, ContentLayer.STUDY_PLAN_TEMPLATES, study_plan_counts[caps_ref], target)

    return result


def _is_approved_blueprint(blueprint: dict[str, Any]) -> bool:
    if blueprint.get("review_status"):
        return blueprint.get("review_status") == "approved"
    return bool(blueprint.get("selection_rules", {}).get("review_status") == "approved")


def _study_plan_counts(payload: dict[str, Any], scope_refs: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in payload.get("topic_sequence", []):
        caps_ref = row.get("caps_ref")
        if caps_ref in scope_refs:
            counts[caps_ref] += 1
    for row in payload.get("remediation_mappings", []):
        caps_ref = row.get("caps_ref")
        if caps_ref in scope_refs:
            counts[caps_ref] += 1
    for row in payload.get("extension_mappings", []):
        caps_ref = row.get("caps_ref")
        if caps_ref in scope_refs:
            counts[caps_ref] += 1
    return counts


def _check_target(
    result: ScopeValidationResult,
    caps_ref: str,
    layer: ContentLayer,
    approved: int,
    target: dict[str, int],
) -> None:
    key = f"{layer.value}.approved"
    expected = int(target.get(key, 0))
    if expected and approved < expected:
        result.errors.append(f"{caps_ref} {layer.value} approved target unmet: {approved}/{expected}")


def print_result(result: ScopeValidationResult) -> None:
    print(f"Scope content validation: {result.scope_id}")
    print(f"  status: {result.status}")
    print(f"  skipped: {result.skipped}")
    print(f"  approved item counts: {result.item_counts}")
    print(f"  approved lesson counts: {result.lesson_counts}")
    print(f"  approved blueprint counts: {result.blueprint_counts}")
    print(f"  study plan counts: {result.study_plan_counts}")
    if result.errors:
        print("Failures:")
        for error in result.errors:
            print(f"  - {error}")
    else:
        print("  status: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", action="append", dest="scope_ids", help="Scope id to validate. Repeatable.")
    parser.add_argument("--all-active", action="store_true", help="Validate every active scope in scopes.json.")
    parser.add_argument("--strict", action="store_true", help="Fail when approved counts do not meet configured targets.")
    args = parser.parse_args()

    registry = ContentScopeRegistry()
    scope_ids = args.scope_ids or []
    if args.all_active:
        scope_ids.extend(scope.scope_id for scope in registry.list_active_scopes())
    if not scope_ids:
        parser.error("provide --scope-id or --all-active")

    results = [validate_scope(scope_id, strict=args.strict, registry=registry) for scope_id in dict.fromkeys(scope_ids)]
    for result in results:
        print_result(result)
    return 1 if any(not result.passed for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
