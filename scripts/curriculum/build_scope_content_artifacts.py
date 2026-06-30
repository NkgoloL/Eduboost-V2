#!/usr/bin/env python3
"""Build registry-driven scope content artifacts.

This is the generic, scope-aware build entrypoint for Content Factory.
It validates source readiness, generates the four learner-facing artifact
layers for a scope, and writes a run manifest alongside the outputs.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.content_coverage import ContentLayer
from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.modules.lessons.lesson_validator import LessonValidator
from app.services.content_generation.generated_item_contract import GeneratedItemQualityValidator
from app.services.content_generation.generated_lesson_contract import GeneratedLessonQualityValidator, LESSON_VARIANTS
from app.services.content_generation.scope_blueprint_generator import ScopeBlueprintGenerator
from app.services.content_generation.scope_item_generator import ITEM_DIFFICULTY_BANDS, ScopeItemGenerator
from app.services.content_generation.scope_lesson_generator import ScopeLessonGenerator
from app.services.content_generation.scope_study_plan_generator import ScopeStudyPlanGenerator
from app.services.content_generation.topic_map_source_context import TopicMapSourceContextBuilder
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_source_manifest import generation_ready, validate_source_manifest

DEFAULT_OUTPUT_ROOT = ROOT
DEFAULT_ITEM_TARGET = 40
DEFAULT_LESSON_TARGET = 8

_LAYER_PATHS = {
    ContentLayer.DIAGNOSTIC_ITEMS: ("items", "item_bank.json"),
    ContentLayer.LESSONS: ("lessons", "lessons.json"),
    ContentLayer.ASSESSMENT_BLUEPRINTS: ("assessment_blueprints", "blueprints.json"),
    ContentLayer.STUDY_PLAN_TEMPLATES: ("study_plans", "templates.json"),
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _scope_output_path(scope: Any, layer: ContentLayer, *, output_root: Path) -> Path:
    configured = getattr(scope, "artifact_paths", {}).get(layer.value)
    if configured:
        return output_root / configured
    folder, filename = _LAYER_PATHS[layer]
    return output_root / "data" / "generated" / folder / f"{scope.scope_id}_{filename}"


def _run_manifest_path(scope_id: str, *, output_root: Path, run_id: uuid.UUID) -> Path:
    return output_root / "data" / "generated" / "run_manifests" / f"{scope_id}_{run_id}.json"


def _cycle(values: tuple[str, ...], index: int) -> str:
    return values[index % len(values)]


def _build_item(
    scope: Any,
    context_payload: dict[str, Any],
    *,
    ref: str,
    index: int,
    sequence: int,
    band: str,
    source_builder: TopicMapSourceContextBuilder,
    item_generator: ScopeItemGenerator,
) -> dict[str, Any]:
    source_result = source_builder.build(
        scope_id=scope.scope_id,
        caps_ref=ref,
        topic_context=context_payload,
        topic_map_path=scope.topic_map_path,
        source_document_ids=list(scope.source_documents or []),
        phase=getattr(scope, "phase", None),
        language=scope.language,
    )
    if not source_result.passed or source_result.context is None:
        raise ValueError(f"Missing or thin source context for {scope.scope_id}/{ref}: {source_result.errors}")
    return item_generator.generate(
        source_result.context,
        index=index,
        sequence=sequence,
        band=band,
        scope_id=scope.scope_id,
    )


def _build_lesson(
    scope: Any,
    context_payload: dict[str, Any],
    *,
    ref: str,
    index: int,
    source_builder: TopicMapSourceContextBuilder,
    lesson_generator: ScopeLessonGenerator,
) -> dict[str, Any]:
    source_result = source_builder.build(
        scope_id=scope.scope_id,
        caps_ref=ref,
        topic_context=context_payload,
        topic_map_path=scope.topic_map_path,
        source_document_ids=list(scope.source_documents or []),
        phase=getattr(scope, "phase", None),
        language=scope.language,
    )
    if not source_result.passed or source_result.context is None:
        raise ValueError(f"Missing or thin source context for {scope.scope_id}/{ref}: {source_result.errors}")
    variant = _cycle(LESSON_VARIANTS, index)
    return lesson_generator.generate(source_result.context, index=index, variant=variant)


def _lesson_validation_payload(lesson: dict[str, Any]) -> dict[str, Any]:
    return dict(lesson)


def _approved_target_for_ref(registry: ContentScopeRegistry, scope_id: str, caps_ref: str, key: str, default: int) -> int:
    for target in registry.get_scope_targets(scope_id):
        if target.caps_ref == caps_ref and key in target.targets:
            return int(target.targets[key])
    return default


def _spread_counts(total: int, buckets: int) -> list[int]:
    base, remainder = divmod(total, buckets)
    return [base + (1 if index < remainder else 0) for index in range(buckets)]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_scope_content_artifacts(
    scope_id: str,
    *,
    output_root: Path | None = None,
    write: bool = True,
    verify_generated_content: bool = True,
    registry: ContentScopeRegistry | None = None,
) -> dict[str, Any]:
    registry = registry or ContentScopeRegistry()
    output_root = output_root or DEFAULT_OUTPUT_ROOT
    scope = registry.get_scope(scope_id)
    source_result = validate_source_manifest(registry=registry)

    if not source_result.passed:
        raise ValueError(f"Source manifest validation failed: {source_result.errors}")
    if not generation_ready(scope_id, registry=registry):
        raise ValueError(f"Scope {scope_id} is not generation-ready from approved source material.")
    if not scope.caps_refs:
        raise ValueError(f"Scope {scope_id} does not declare CAPS references.")
    if not scope.topic_map_path:
        raise ValueError(f"Scope {scope_id} does not declare a topic_map_path.")

    topic_map_path = ROOT / scope.topic_map_path
    if not topic_map_path.exists():
        raise FileNotFoundError(topic_map_path)

    topic_map_service = CAPSTopicMapService(map_paths=[topic_map_path])
    topic_map = json.loads(topic_map_path.read_text(encoding="utf-8"))
    item_validator = ItemValidator(topic_map=topic_map)
    lesson_validator = LessonValidator(caps_service=topic_map_service)
    lesson_quality_validator = GeneratedLessonQualityValidator()
    item_quality_validator = GeneratedItemQualityValidator()
    source_builder = TopicMapSourceContextBuilder(project_root=ROOT)
    item_generator = ScopeItemGenerator()
    lesson_generator = ScopeLessonGenerator()
    blueprint_generator = ScopeBlueprintGenerator()
    study_plan_generator = ScopeStudyPlanGenerator()
    source_context_hashes: dict[str, str] = {}

    contexts: dict[str, dict[str, Any]] = {}
    for ref in scope.caps_refs:
        context = topic_map_service.get_topic_context(ref)
        if context is None:
            raise ValueError(f"Topic map {scope.topic_map_path} does not resolve CAPS ref {ref}.")
        contexts[ref] = context

    item_counts: Counter[str] = Counter()
    lesson_counts: Counter[str] = Counter()
    item_errors: list[str] = []
    lesson_errors: list[str] = []
    generated_items: list[dict[str, Any]] = []
    generated_lessons: list[dict[str, Any]] = []

    for ref in scope.caps_refs:
        item_target = _approved_target_for_ref(
            registry,
            scope_id,
            ref,
            "diagnostic_items.approved",
            DEFAULT_ITEM_TARGET,
        )
        lesson_target = _approved_target_for_ref(
            registry,
            scope_id,
            ref,
            "lessons.approved",
            DEFAULT_LESSON_TARGET,
        )

        item_bands = _spread_counts(item_target, len(ITEM_DIFFICULTY_BANDS))
        item_sequence = 0
        for band, band_count in zip(ITEM_DIFFICULTY_BANDS, item_bands):
            for index in range(band_count):
                item = _build_item(
                    scope,
                    contexts[ref],
                    ref=ref,
                    index=index,
                    sequence=item_sequence,
                    band=band,
                    source_builder=source_builder,
                    item_generator=item_generator,
                )
                item_sequence += 1
                validation_errors = item_validator.validate_all(item)
                if validation_errors:
                    item_errors.append(f"{ref}/{item['item_id']}: {[error.rule for error in validation_errors]}")
                quality_issues = item_quality_validator.validate_item(item)
                if quality_issues:
                    item_errors.append(
                        f"{ref}/{item['item_id']}: {[f'{issue.field}: {issue.reason}' for issue in quality_issues]}"
                    )
                generated_items.append(item)
                item_counts[ref] += 1

        for index in range(lesson_target):
            lesson = _build_lesson(
                scope,
                contexts[ref],
                ref=ref,
                index=index,
                source_builder=source_builder,
                lesson_generator=lesson_generator,
            )
            source_context_hashes[ref] = str(lesson.get("source_context_hash") or "")
            validation = lesson_validator.validate(_lesson_validation_payload(lesson), require_verified=True)
            if not validation.passed:
                lesson_errors.append(f"{ref}/{lesson['lesson_id']}: {validation.failures}")
            quality_issues = lesson_quality_validator.validate_lesson(
                lesson,
                scope_id=scope.scope_id,
                subject_code=scope.subject_code,
                subject=scope.subject,
                source_document_ids=list(scope.source_documents or []),
            )
            if quality_issues:
                lesson_errors.append(
                    f"{ref}/{lesson['lesson_id']}: {[f'{issue.field}: {issue.reason}' for issue in quality_issues]}"
                )
            generated_lessons.append(lesson)
            lesson_counts[ref] += 1

    item_payload_for_quality = {"items": generated_items}
    file_item_issues = item_quality_validator.validate_file_payload(item_payload_for_quality)
    if file_item_issues.issues:
        item_errors.append(
            f"item_bank: {[f'{issue.item_id}/{issue.field}: {issue.reason}' for issue in file_item_issues.issues[:5]]}"
        )

    blueprints = blueprint_generator.generate(
        scope_id,
        list(scope.caps_refs),
        contexts,
        source_context_hashes=source_context_hashes,
    )
    study_plans = study_plan_generator.generate(
        scope_id,
        list(scope.caps_refs),
        contexts,
        source_context_hashes=source_context_hashes,
    )

    blueprint_errors: list[str] = []
    blueprint_refs = {
        ref for blueprint in blueprints["blueprints"] for ref in blueprint.get("selection_rules", {}).get("caps_refs", [])
    }
    if not blueprint_refs <= set(scope.caps_refs):
        blueprint_errors.append(f"blueprint refs outside scope: {sorted(blueprint_refs - set(scope.caps_refs))}")

    template_refs = {
        row.get("caps_ref")
        for row in study_plans["topic_sequence"]
        if row.get("caps_ref")
    } | {
        row.get("caps_ref")
        for row in study_plans["remediation_mappings"]
        if row.get("caps_ref")
    } | {
        row.get("caps_ref")
        for row in study_plans["extension_mappings"]
        if row.get("caps_ref")
    }
    study_plan_errors: list[str] = []
    if template_refs != set(scope.caps_refs):
        study_plan_errors.append(
            f"study plan does not cover all CAPS refs: missing={sorted(set(scope.caps_refs) - template_refs)}"
        )

    if verify_generated_content and (item_errors or lesson_errors or blueprint_errors or study_plan_errors):
        raise ValueError(
            "Generated scope content failed validation: "
            f"items={item_errors}, lessons={lesson_errors}, blueprints={blueprint_errors}, study_plans={study_plan_errors}"
        )

    item_path = _scope_output_path(scope, ContentLayer.DIAGNOSTIC_ITEMS, output_root=output_root)
    lesson_path = _scope_output_path(scope, ContentLayer.LESSONS, output_root=output_root)
    blueprint_path = _scope_output_path(scope, ContentLayer.ASSESSMENT_BLUEPRINTS, output_root=output_root)
    study_plan_path = _scope_output_path(scope, ContentLayer.STUDY_PLAN_TEMPLATES, output_root=output_root)
    run_id = uuid.uuid4()
    run_manifest_path = _run_manifest_path(scope_id, output_root=output_root, run_id=run_id)

    item_payload = {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "scope": scope_id,
        "language": scope.language,
        "approval_policy": "auto_approved_when_schema_caps_safety_answer_quality_pass",
        "generator_version": "scope_content_v2",
        "items": generated_items,
    }
    lesson_payload = {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "scope": scope_id,
        "language": scope.language,
        "approval_policy": "auto_approved_when_schema_caps_safety_answer_quality_pass",
        "generator_version": "scope_content_v2",
        "lessons": generated_lessons,
    }

    output_files = {
        "diagnostic_items": str(item_path.relative_to(output_root)),
        "lessons": str(lesson_path.relative_to(output_root)),
        "assessment_blueprints": str(blueprint_path.relative_to(output_root)),
        "study_plan_templates": str(study_plan_path.relative_to(output_root)),
        "run_manifest": str(run_manifest_path.relative_to(output_root)),
    }

    if write:
        _write_json(item_path, item_payload)
        _write_json(lesson_path, lesson_payload)
        _write_json(blueprint_path, blueprints)
        _write_json(study_plan_path, study_plans)

    run_manifest = {
        "schema_version": "1.0",
        "generated_at": _now_utc(),
        "run_id": str(run_id),
        "scope_id": scope_id,
        "grade": scope.grade,
        "phase": scope.phase,
        "subject_code": scope.subject_code,
        "subject": scope.subject,
        "language": scope.language,
        "generator_version": "scope_content_v2",
        "generation_ready": generation_ready(scope_id, registry=registry),
        "source_manifest_validation_passed": source_result.passed,
        "source_manifest_errors": source_result.errors,
        "item_counts": dict(item_counts),
        "lesson_counts": dict(lesson_counts),
        "blueprint_count": len(blueprints["blueprints"]),
        "study_plan_counts": {
            "topic_sequence": len(study_plans["topic_sequence"]),
            "remediation_mappings": len(study_plans["remediation_mappings"]),
            "extension_mappings": len(study_plans["extension_mappings"]),
        },
        "source_context_hashes": source_context_hashes,
        "output_files": output_files,
        "validation": {
            "items": item_errors,
            "lessons": lesson_errors,
            "blueprints": blueprint_errors,
            "study_plans": study_plan_errors,
        },
    }

    if write:
        _write_json(run_manifest_path, run_manifest)

    return {
        "schema_version": "1.0",
        "scope_id": scope_id,
        "generated_at": run_manifest["generated_at"],
        "generation_ready": run_manifest["generation_ready"],
        "source_manifest_validation_passed": run_manifest["source_manifest_validation_passed"],
        "output_files": output_files,
        "item_counts": dict(item_counts),
        "lesson_counts": dict(lesson_counts),
        "blueprint_count": len(blueprints["blueprints"]),
        "study_plan_counts": run_manifest["study_plan_counts"],
        "source_context_hashes": source_context_hashes,
        "validation": run_manifest["validation"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", required=True, help="Registry scope to build.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory for generated artifact paths.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and plan the build without writing files.")
    parser.add_argument("--json", action="store_true", help="Emit the build manifest as JSON.")
    args = parser.parse_args()

    report = build_scope_content_artifacts(
        args.scope_id,
        output_root=args.output_root,
        write=not args.dry_run,
    )
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Scope build: {report['scope_id']}")
        print(f"  generation_ready: {report['generation_ready']}")
        print(f"  item counts: {report['item_counts']}")
        print(f"  lesson counts: {report['lesson_counts']}")
        print(f"  output files: {report['output_files']}")
    return 0 if not any(report["validation"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
