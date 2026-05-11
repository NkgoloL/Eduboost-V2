#!/usr/bin/env python3
"""Validate diagnostics, item-bank, practice, and mastery evidence wiring."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/learning_science/irt_model.md",
    "docs/learning_science/mastery_model.md",
    "docs/diagnostics/item_contract.md",
    "docs/caps/grade4_maths_coverage_matrix.md",
    "docs/caps/grade4_maths_120_item_production_plan.md",
    "docs/learning_science/learning_evidence.md",
    "app/domain/item_schema.py",
    "app/models/diagnostic_item.py",
    "app/models/item_exposure.py",
    "app/modules/diagnostics/irt_engine.py",
    "app/modules/diagnostics/item_bank_service.py",
    "app/modules/diagnostics/diagnostic_session_service.py",
    "app/modules/diagnostics/session_recovery_service.py",
    "app/modules/diagnostics/calibration_service.py",
    "app/modules/practice/practice_generator.py",
    "app/modules/practice/spaced_repetition_scheduler.py",
    "app/modules/progress/mastery_model.py",
    "app/modules/progress/learning_velocity_service.py",
    "scripts/ci/check_diagnostics_assessment.py",
    "scripts/validate_item_bank.py",
    "tests/unit/modules/diagnostics/test_irt_engine_hardening.py",
    "tests/unit/modules/diagnostics/test_item_bank_models.py",
    "tests/unit/modules/diagnostics/test_item_bank_service.py",
    "tests/unit/modules/diagnostics/test_session_lifecycle.py",
    "tests/unit/modules/practice/test_practice_and_calibration.py",
    "tests/unit/modules/progress/test_mastery_model.py",
    "tests/unit/test_learning_evidence.py",
)

CONTENT_REQUIREMENTS = {
    "docs/learning_science/learning_evidence.md": (
        "Item Schema",
        "IRT Validation",
        "Item Bank Approval Scope",
        "Diagnostic Session Lifecycle",
        "Mastery Evidence",
        "make learning-evidence-check",
        "Verification Gaps",
    ),
    "docs/caps/grade4_maths_coverage_matrix.md": (
        "Current Approved Items",
        "14 approved starter items",
        "approval gate remains open",
    ),
    "Makefile": (
        "diagnostics-assessment-check",
        "learning-evidence-check",
    ),
}


@dataclass(frozen=True)
class EvidenceResult:
    target: str
    ok: bool
    detail: str


def check_all() -> list[EvidenceResult]:
    results: list[EvidenceResult] = []
    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                EvidenceResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )
    return results


def main() -> int:
    results = check_all()
    print("Learning evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
