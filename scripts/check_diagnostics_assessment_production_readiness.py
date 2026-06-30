#!/usr/bin/env python3
"""Validate production-readiness item 07 diagnostics/assessment evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "app/domain/item_schema.py",
    "app/modules/diagnostics/production_readiness_contracts.py",
    "app/modules/diagnostics/irt_engine.py",
    "app/modules/diagnostics/diagnostic_session_service.py",
    "app/modules/diagnostics/session_recovery_service.py",
    "app/modules/diagnostics/termination_service.py",
    "app/modules/diagnostics/item_bank_service.py",
    "app/modules/diagnostics/item_selection_service.py",
    "app/modules/diagnostics/calibration_service.py",
    "app/modules/diagnostics/item_validator.py",
    "app/modules/diagnostics/bias_review_router.py",
    "app/modules/practice/practice_generator.py",
    "app/modules/practice/spaced_repetition_scheduler.py",
    "app/modules/progress/mastery_model.py",
    "app/modules/progress/learning_velocity_service.py",
    "docs/diagnostics/production_diagnostics_assessment_readiness_contract.md",
    "docs/diagnostics/item_bank_launch_coverage_contract.md",
    "docs/diagnostics/mastery_model_assessment_contract.md",
    "docs/diagnostics/assessment_quality_fairness_contract.md",
    "docs/backlog/production_readiness/07_diagnostics_assessment_item_bank_and_mastery_model.md",
    "tests/unit/test_diagnostics_assessment_production_readiness.py",
    "tests/unit/modules/diagnostics/test_irt_engine_hardening.py",
    "tests/unit/modules/diagnostics/test_session_lifecycle.py",
    "tests/unit/modules/diagnostics/test_item_bank_models.py",
    "tests/unit/modules/diagnostics/test_item_bank_service.py",
    "tests/unit/modules/diagnostics/test_item_validator.py",
    "tests/unit/modules/progress/test_mastery_model.py",
    "tests/unit/modules/practice/test_practice_and_calibration.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/diagnostics/production_readiness_contracts.py": (
        "DiagnosticItemSpec",
        "ItemReviewStatus",
        "grade_equivalent_from_theta",
        "select_item_by_fisher_information",
        "identify_gap_topics",
        "audit_minimum_viable_item_bank",
        "required_bias_review_dimensions",
        "remediation_tags_from_misconceptions",
    ),
    "docs/diagnostics/production_diagnostics_assessment_readiness_contract.md": (
        "grade-equivalent mapping evidence",
        "item selection by Fisher information evidence",
        "gap identification evidence",
        "pause/resume, session recovery, maximum item cap, minimum evidence threshold, and confidence interval evidence",
    ),
    "docs/diagnostics/item_bank_launch_coverage_contract.md": (
        "minimum viable item bank for each supported launch grade",
        "item review status `draft`",
        "item review status `AI-generated`",
        "item review status `human-reviewed`",
        "item review status `approved`",
        "item review status `retired`",
        "item retirement workflow",
        "item import/export tooling",
    ),
    "docs/diagnostics/mastery_model_assessment_contract.md": (
        "remediation based on misconception",
        "spaced repetition",
        "retrieval practice",
        "learning velocity",
        "risk-of-falling-behind signal",
        "next-best-activity recommendation",
        "Bayesian Knowledge Tracing and Deep Knowledge Tracing remain post-launch research tracks",
    ),
    "docs/diagnostics/assessment_quality_fairness_contract.md": (
        "item bias review across language",
        "item bias review across region",
        "item bias review across socioeconomic context",
        "distractor quality review",
        "explanation quality review",
        "educator sign-off process",
    ),
    "docs/backlog/production_readiness/07_diagnostics_assessment_item_bank_and_mastery_model.md": (
        "7.6 Repository-side implementation evidence",
        "diagnostics-assessment-production-readiness-check",
        "Research items remain outstanding until sufficient usage data exists",
    ),
    "Makefile": (
        "diagnostics-assessment-production-readiness-check:",
        "scripts/check_diagnostics_assessment_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class CheckResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []
    for rel_path in REQUIRED_FILES:
        path = ROOT / rel_path
        results.append(CheckResult(rel_path, path.exists(), "present" if path.exists() else "missing"))
    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                CheckResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )
    return results


def main() -> int:
    results = run_checks()
    print("Diagnostics assessment production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
