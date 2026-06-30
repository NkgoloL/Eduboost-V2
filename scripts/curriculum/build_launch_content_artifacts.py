#!/usr/bin/env python3
"""Compatibility wrapper for the Grade 4 Maths launch content build.

The underlying generation logic now lives in the registry-driven scope
builder. This wrapper keeps the legacy launch-side sidecar artifacts in
place for docs and scripts that still refer to them.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.build_scope_content_artifacts import build_scope_content_artifacts

DEFAULT_SCOPE_ID = "grade4_mathematics_en"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _build_coverage_targets(scope_id: str, registry: ContentScopeRegistry, *, generated_at: str) -> dict[str, Any]:
    scope = registry.get_scope(scope_id)
    targets: list[dict[str, Any]] = []
    for ref in scope.caps_refs:
        per_ref_targets = {}
        for target in registry.get_scope_targets(scope_id):
            if target.caps_ref == ref:
                per_ref_targets = dict(target.targets)
                break
        targets.append(
            {
                "caps_ref": ref,
                "grade": scope.grade,
                "subject": scope.subject,
                "term": None,
                "topic": None,
                "diagnostic_items_approved": int(per_ref_targets.get("diagnostic_items.approved", 40)),
                "diagnostic_items_max_candidates": int(per_ref_targets.get("diagnostic_items.approved", 40)) + 35,
                "lesson_plans_approved": int(per_ref_targets.get("lessons.approved", 8)),
                "assessment_blueprints": [
                    "baseline_diagnostic",
                    "topic_diagnostic",
                    "short_practice_quiz",
                    "recheck_assessment",
                ],
            }
        )
    return {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "scope": f"{scope_id}_launch_slice",
        "language": scope.language,
        "review_policy": {
            "auto_approve_threshold": 0.85,
            "review_threshold": 0.70,
            "requires_answer_key_verification": True,
            "requires_safety_passed": True,
        },
        "targets": targets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", default=DEFAULT_SCOPE_ID, help="Registry scope to build.")
    parser.add_argument("--json", action="store_true", help="Emit the compatibility manifest as JSON.")
    args = parser.parse_args()

    registry = ContentScopeRegistry()
    report = build_scope_content_artifacts(args.scope_id, write=True, registry=registry)
    scope = registry.get_scope(args.scope_id)

    coverage = _build_coverage_targets(args.scope_id, registry, generated_at=report["generated_at"])
    _write_json(ROOT / "data" / "caps" / "launch_coverage_targets.json", coverage)

    manifest = {
        "operation": "build_launch_content_artifacts",
        "generated_at": report["generated_at"],
        "provider": "generic_scope_builder",
        "model": "scope-scaffold",
        "curriculum_version": "caps-mvp-2026.05",
        "caps_refs": scope.caps_refs,
        "artifact_counts": {
            "coverage_targets": len(coverage["targets"]),
            "assessment_blueprints": report["blueprint_count"],
            "study_plan_topics": len(scope.caps_refs),
            "lessons": sum(report["lesson_counts"].values()),
        },
        "output_files": report["output_files"],
    }
    _write_json(ROOT / "data" / "generated" / "run_manifests" / "launch_content_artifacts.json", manifest)

    if args.json:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0 if not any(report["validation"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
