#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "docs/caps/grade4_maths_coverage_matrix.md",
    "docs/caps/grade4_maths_120_item_production_plan.md",
    "docs/diagnostics/item_contract.md",
    "docs/learning_science/irt_model.md",
    "docs/learning_science/mastery_model.md",
    "scripts/validate_item_bank.py",
    "scripts/ci/check_diagnostics_assessment.py",
    "tests/unit/modules/diagnostics/test_item_bank_service.py",
    "tests/unit/modules/diagnostics/test_irt_engine_hardening.py",
    "tests/unit/modules/progress/test_mastery_model.py",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    results = [Result(p, (ROOT / p).exists(), "present" if (ROOT / p).exists() else "missing") for p in REQUIRED]
    matrix = (ROOT / "docs/caps/grade4_maths_coverage_matrix.md").read_text(encoding="utf-8")
    for snippet in ("Current approved items per launch ref", "40 approved", "Green for launch slice"):
        results.append(Result("docs/caps/grade4_maths_coverage_matrix.md", snippet in matrix, f"contains {snippet!r}"))
    return results


def main() -> int:
    results = check_all()
    print("CAPS learning proof check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
