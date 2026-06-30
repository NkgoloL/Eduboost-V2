#!/usr/bin/env python3
"""Validate AI refusal regression fixtures."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "ai" / "refusals"
DOC = REPO_ROOT / "docs" / "ai" / "ai_refusal_regression_fixtures.md"

REQUIRED_FIXTURES = (
    "unsafe_instruction_refusal.json",
    "privacy_leakage_refusal.json",
    "hidden_prompt_refusal.json",
)
REQUIRED_FIELDS = (
    "case_id",
    "category",
    "safety_status",
    "refusal_reason",
    "safe_educational_redirection",
    "no_unsafe_operational_detail",
    "no_hidden_prompt_disclosure",
)


@dataclass(frozen=True)
class RefusalFixtureResult:
    fixture: str
    ok: bool
    detail: str


def _load(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def validate_fixture(name: str) -> list[RefusalFixtureResult]:
    path = FIXTURE_DIR / name
    if not path.exists():
        return [RefusalFixtureResult(name, False, "fixture missing")]
    data = _load(path)
    if data is None:
        return [RefusalFixtureResult(name, False, "invalid json")]

    results: list[RefusalFixtureResult] = []
    for field in REQUIRED_FIELDS:
        results.append(
            RefusalFixtureResult(
                name,
                field in data,
                f"contains {field!r}" if field in data else f"missing {field!r}",
            )
        )

    results.append(
        RefusalFixtureResult(
            name,
            data.get("safety_status") == "refused",
            "safety_status refused" if data.get("safety_status") == "refused" else "safety_status not refused",
        )
    )
    results.append(
        RefusalFixtureResult(
            name,
            data.get("no_unsafe_operational_detail") is True and data.get("no_hidden_prompt_disclosure") is True,
            "refusal suppresses unsafe detail and hidden prompt disclosure"
            if data.get("no_unsafe_operational_detail") is True and data.get("no_hidden_prompt_disclosure") is True
            else "refusal safety booleans invalid",
        )
    )
    return results


def run_checks() -> list[RefusalFixtureResult]:
    results: list[RefusalFixtureResult] = []
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results.append(RefusalFixtureResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing"))
    for snippet in ("AI Refusal Regression Fixtures", "unsafe instruction", "privacy leakage", "hidden prompt disclosure", "make ai-refusal-fixture-check"):
        results.append(RefusalFixtureResult(str(DOC.relative_to(REPO_ROOT)), snippet in doc_text, f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}"))
    for fixture in REQUIRED_FIXTURES:
        results.extend(validate_fixture(fixture))
    return results


def main() -> int:
    results = run_checks()
    print("AI refusal fixture check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.fixture}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
