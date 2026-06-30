#!/usr/bin/env python3
"""Validate frontend mock API fixtures for Playwright journeys."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "frontend" / "api"
DOC = REPO_ROOT / "docs" / "frontend" / "playwright_mock_api_fixtures.md"

SUCCESS_FIXTURES = (
    "learner_dashboard_success.json",
    "diagnostic_submit_success.json",
    "lesson_generation_success.json",
    "parent_dashboard_success.json",
)
ERROR_FIXTURES = (
    "consent_denied_error.json",
    "authorization_denied_error.json",
)


@dataclass(frozen=True)
class FrontendMockApiFixtureResult:
    fixture: str
    ok: bool
    detail: str


def _load(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _validate_success(name: str) -> list[FrontendMockApiFixtureResult]:
    path = FIXTURE_DIR / name
    if not path.exists():
        return [FrontendMockApiFixtureResult(name, False, "fixture missing")]
    data = _load(path)
    if data is None:
        return [FrontendMockApiFixtureResult(name, False, "invalid json")]

    return [
        FrontendMockApiFixtureResult(name, data.get("ok") is True, "ok true" if data.get("ok") is True else "ok not true"),
        FrontendMockApiFixtureResult(name, isinstance(data.get("data"), dict), "data object present" if isinstance(data.get("data"), dict) else "data object missing"),
        FrontendMockApiFixtureResult(name, bool((data.get("meta") or {}).get("request_id")), "request id present" if bool((data.get("meta") or {}).get("request_id")) else "request id missing"),
    ]


def _validate_error(name: str) -> list[FrontendMockApiFixtureResult]:
    path = FIXTURE_DIR / name
    if not path.exists():
        return [FrontendMockApiFixtureResult(name, False, "fixture missing")]
    data = _load(path)
    if data is None:
        return [FrontendMockApiFixtureResult(name, False, "invalid json")]

    error = data.get("error") or {}
    return [
        FrontendMockApiFixtureResult(name, data.get("ok") is False, "ok false" if data.get("ok") is False else "ok not false"),
        FrontendMockApiFixtureResult(name, bool(error.get("code")), "error code present" if bool(error.get("code")) else "error code missing"),
        FrontendMockApiFixtureResult(name, bool(error.get("message")), "error message present" if bool(error.get("message")) else "error message missing"),
        FrontendMockApiFixtureResult(name, bool(error.get("safe_next_action")), "safe next action present" if bool(error.get("safe_next_action")) else "safe next action missing"),
        FrontendMockApiFixtureResult(name, bool((data.get("meta") or {}).get("request_id")), "request id present" if bool((data.get("meta") or {}).get("request_id")) else "request id missing"),
    ]


def run_checks() -> list[FrontendMockApiFixtureResult]:
    results: list[FrontendMockApiFixtureResult] = []
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    results.append(
        FrontendMockApiFixtureResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing")
    )

    for snippet in (
        "Playwright Mock API Fixtures",
        "Success Fixtures",
        "Denial Fixtures",
        "error.safe_next_action",
        "make frontend-mock-api-fixture-check",
    ):
        results.append(
            FrontendMockApiFixtureResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for fixture in SUCCESS_FIXTURES:
        results.extend(_validate_success(fixture))
    for fixture in ERROR_FIXTURES:
        results.extend(_validate_error(fixture))

    return results


def main() -> int:
    results = run_checks()
    print("Frontend mock API fixture check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.fixture}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
