#!/usr/bin/env python3
"""Validate mocked Playwright journey specs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "tests/e2e/learner-mocked-api-journey.spec.ts",
    "tests/e2e/parent-mocked-api-journey.spec.ts",
    "docs/frontend/playwright_mocked_journey_specs.md",
)

CONTENT_REQUIREMENTS = {
    "tests/e2e/learner-mocked-api-journey.spec.ts": (
        "mockLearnerJourneyApi",
        "mockConsentDeniedApi",
        "learner journey with mocked API",
        "toBeGreaterThan(0)",
    ),
    "tests/e2e/parent-mocked-api-journey.spec.ts": (
        "mockParentJourneyApi",
        "mockAuthorizationDeniedApi",
        "parent journey with mocked API",
        "toBeGreaterThan(0)",
    ),
    "docs/frontend/playwright_mocked_journey_specs.md": (
        "Playwright Mocked Journey Specs",
        "learner consent denial envelope",
        "parent authorization denial envelope",
        "must not require live learner data",
        "make frontend-playwright-mocked-specs-check",
    ),
}


@dataclass(frozen=True)
class MockedSpecResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[MockedSpecResult]:
    results: list[MockedSpecResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(MockedSpecResult(rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                MockedSpecResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend Playwright mocked specs check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
