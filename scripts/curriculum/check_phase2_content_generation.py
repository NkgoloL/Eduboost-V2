#!/usr/bin/env python3
"""Verify Phase 2 generated-content evidence without writing manifests."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_file_artifact_import import ContentFileArtifactImportService
from app.services.content_file_lesson_quality import ContentFileLessonQualityService
from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService
from app.services.content_scope_registry import ContentScopeRegistry

GENERATED_DIR = ROOT / "data" / "generated"


@dataclass
class Phase2ContentCheckResult:
    failures: list[str] = field(default_factory=list)
    facts: dict[str, object] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.failures

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)


def check_phase2_content_generation() -> Phase2ContentCheckResult:
    result = Phase2ContentCheckResult()
    registry = ContentScopeRegistry(project_root=ROOT)

    generated_files = sorted(GENERATED_DIR.rglob("*")) if GENERATED_DIR.exists() else []
    generated_file_count = sum(1 for path in generated_files if path.is_file())
    result.facts["generated_file_count"] = generated_file_count
    result.require(GENERATED_DIR.exists(), "data/generated is missing from the main WSL working directory")
    result.require(generated_file_count >= 400, f"expected restored generated artifact set, found {generated_file_count} files")

    lesson_quality = ContentFileLessonQualityService(project_root=ROOT, registry=registry).build_all()["summary"]
    result.facts["lesson_quality"] = lesson_quality
    result.require(lesson_quality["lesson_files_present"] == 51, "expected 51 generated lesson files")
    result.require(lesson_quality["total_lessons"] >= 150, "expected at least 150 generated lessons")
    result.require(lesson_quality["failed_lessons"] == 0, "generated lessons must have zero quality failures")
    result.require(lesson_quality["lesson_layers_quarantined"] == 0, "lesson layers must not be quarantined")

    import_plan = ContentFileArtifactImportService(project_root=ROOT, registry=registry).plan_scope_imports(
        statuses={"review"}
    ).to_manifest()["summary"]
    result.facts["review_scope_import_plan"] = import_plan
    result.require(import_plan["scope_count"] == 50, "expected 50 review scopes in import plan")
    result.require(import_plan["stage_unlocked"] == 50, "expected all 50 review scopes to be staging-unlocked")
    result.require(import_plan["scopes_with_errors"] == 0, "review-scope import plan must have zero scope errors")
    result.require(import_plan["total_records"] >= 150, "review-scope import plan must include generated lesson/content records")
    result.require(import_plan["production_unlocked"] == 0, "review scopes must remain production-locked without real approvals")

    promotion = ContentFilePromotionReadinessService(project_root=ROOT, registry=registry).build_all()["summary"]
    result.facts["promotion_readiness"] = promotion
    result.require(promotion["scope_count"] == 51, "expected 51 total scopes in promotion readiness")
    result.require(promotion["staging_eligible"] == 51, "expected restored artifacts to make all scopes staging-eligible")
    result.require(promotion["review_blocked"] == 50, "expected 50 review scopes blocked from production")
    result.require(promotion["lesson_quarantined"] == 0, "expected no lesson layers quarantined after regeneration")
    return result


def print_result(result: Phase2ContentCheckResult) -> None:
    print("Phase 2 generated-content evidence check")
    for key, value in result.facts.items():
        print(f"- INFO {key}: {value}")
    if result.failures:
        for failure in result.failures:
            print(f"- FAIL {failure}")
    else:
        print("- PASS generated artifact set is present in the main WSL working directory")
        print("- PASS generated lessons satisfy the current quality contract")
        print("- PASS review-scope import planning is clean and production remains approval-gated")


def main() -> int:
    result = check_phase2_content_generation()
    print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
