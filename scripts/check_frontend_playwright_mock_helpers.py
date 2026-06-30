#!/usr/bin/env python3
"""Validate Playwright mock API route helper evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "tests" / "e2e" / "support" / "mockApi.ts"
DOC = REPO_ROOT / "docs" / "frontend" / "playwright_mock_route_helpers.md"

HELPER_SNIPPETS = (
    "loadApiFixture",
    "mockJson",
    "mockLearnerJourneyApi",
    "mockParentJourneyApi",
    "mockConsentDeniedApi",
    "mockAuthorizationDeniedApi",
    "learner_dashboard_success.json",
    "authorization_denied_error.json",
    "route.fulfill",
)

DOC_SNIPPETS = (
    "Playwright Mock Route Helpers",
    "canonical API fixture envelopes",
    "mockLearnerJourneyApi",
    "mockParentJourneyApi",
    "mockConsentDeniedApi",
    "make frontend-playwright-mock-helper-check",
)


@dataclass(frozen=True)
class MockHelperResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[MockHelperResult]:
    helper_text = HELPER.read_text(encoding="utf-8") if HELPER.exists() else ""
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        MockHelperResult(str(HELPER.relative_to(REPO_ROOT)), HELPER.exists(), "helper present" if HELPER.exists() else "helper missing"),
        MockHelperResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing"),
    ]

    for snippet in HELPER_SNIPPETS:
        results.append(
            MockHelperResult(
                str(HELPER.relative_to(REPO_ROOT)),
                snippet in helper_text,
                f"contains {snippet!r}" if snippet in helper_text else f"missing {snippet!r}",
            )
        )

    for snippet in DOC_SNIPPETS:
        results.append(
            MockHelperResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend Playwright mock helper check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
