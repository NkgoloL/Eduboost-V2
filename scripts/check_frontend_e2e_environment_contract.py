#!/usr/bin/env python3
"""Validate frontend E2E environment contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_e2e_environment_contract.md"
CONFIG = REPO_ROOT / "playwright.config.ts"

DOC_SNIPPETS = (
    "Frontend E2E Environment Contract",
    "FRONTEND_BASE_URL",
    "PLAYWRIGHT_WEB_SERVER_COMMAND",
    "LEARNER_JOURNEY_PATH",
    "PARENT_JOURNEY_PATH",
    "PLAYWRIGHT_MOCK_API",
    "frontend base URL must point to a running frontend server",
    "mocked API mode must not call production backend services",
    "runtime E2E must not require live learner or parent data",
    "traces and screenshots must be retained on failure",
    "make frontend-e2e-env-contract-check",
)

CONFIG_SNIPPETS = (
    "FRONTEND_BASE_URL",
    "PLAYWRIGHT_WEB_SERVER_COMMAND",
    "trace: \"retain-on-failure\"",
    "screenshot: \"only-on-failure\"",
)


@dataclass(frozen=True)
class FrontendE2EEnvResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[FrontendE2EEnvResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    config_text = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""

    results = [
        FrontendE2EEnvResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "contract present" if DOC.exists() else "contract missing"),
        FrontendE2EEnvResult(str(CONFIG.relative_to(REPO_ROOT)), CONFIG.exists(), "Playwright config present" if CONFIG.exists() else "Playwright config missing"),
    ]

    for snippet in DOC_SNIPPETS:
        results.append(
            FrontendE2EEnvResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in CONFIG_SNIPPETS:
        results.append(
            FrontendE2EEnvResult(
                str(CONFIG.relative_to(REPO_ROOT)),
                snippet in config_text,
                f"contains {snippet!r}" if snippet in config_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend E2E environment contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
