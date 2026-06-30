#!/usr/bin/env python3
"""Validate frontend journey fixtures for future Playwright coverage."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "frontend"
DOC = REPO_ROOT / "docs" / "frontend" / "playwright_journey_fixture_contract.md"

REQUIRED_FIXTURES = (
    "learner_journey_fixture.json",
    "parent_journey_fixture.json",
)

COMMON_FIELDS = (
    "journey",
    "actor",
    "steps",
    "required_api_domains",
    "denial_states",
)


@dataclass(frozen=True)
class FrontendJourneyFixtureResult:
    fixture: str
    ok: bool
    detail: str


def _load(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def validate_fixture(name: str) -> list[FrontendJourneyFixtureResult]:
    path = FIXTURE_DIR / name
    if not path.exists():
        return [FrontendJourneyFixtureResult(name, False, "fixture missing")]

    data = _load(path)
    if data is None:
        return [FrontendJourneyFixtureResult(name, False, "invalid json")]

    results: list[FrontendJourneyFixtureResult] = []
    for field in COMMON_FIELDS:
        results.append(
            FrontendJourneyFixtureResult(
                name,
                field in data,
                f"contains {field!r}" if field in data else f"missing {field!r}",
            )
        )

    results.append(
        FrontendJourneyFixtureResult(
            name,
            isinstance(data.get("steps"), list) and len(data.get("steps", [])) >= 5,
            "has vertical journey steps" if isinstance(data.get("steps"), list) and len(data.get("steps", [])) >= 5 else "missing vertical journey steps",
        )
    )

    results.append(
        FrontendJourneyFixtureResult(
            name,
            isinstance(data.get("denial_states"), list) and len(data.get("denial_states", [])) >= 3,
            "has denial states" if isinstance(data.get("denial_states"), list) and len(data.get("denial_states", [])) >= 3 else "missing denial states",
        )
    )

    return results


def run_checks() -> list[FrontendJourneyFixtureResult]:
    results: list[FrontendJourneyFixtureResult] = []
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    results.append(
        FrontendJourneyFixtureResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing")
    )

    for snippet in (
        "Playwright Journey Fixture Contract",
        "learner vertical journey fixture",
        "parent vertical journey fixture",
        "consent and authorization denial states",
        "make frontend-journey-fixture-check",
    ):
        results.append(
            FrontendJourneyFixtureResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for fixture in REQUIRED_FIXTURES:
        results.extend(validate_fixture(fixture))

    return results


def main() -> int:
    results = run_checks()
    print("Frontend journey fixture check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.fixture}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
