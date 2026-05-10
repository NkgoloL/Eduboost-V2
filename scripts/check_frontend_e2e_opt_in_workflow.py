#!/usr/bin/env python3
"""Validate frontend E2E opt-in workflow evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "frontend-e2e-opt-in.yml"
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_e2e_opt_in_workflow.md"

WORKFLOW_SNIPPETS = (
    "workflow_dispatch:",
    "frontend_base_url",
    "learner_path",
    "parent_path",
    "web_server_command",
    "FRONTEND_BASE_URL",
    "LEARNER_JOURNEY_PATH",
    "PARENT_JOURNEY_PATH",
    "PLAYWRIGHT_WEB_SERVER_COMMAND",
    "make frontend-e2e-mocked",
    "make frontend-e2e-smoke",
)

DOC_SNIPPETS = (
    "Frontend E2E Opt-In Workflow",
    ".github/workflows/frontend-e2e-opt-in.yml",
    "make frontend-e2e-mocked",
    "make frontend-e2e-smoke",
    "must not run automatically on every pull request",
    "must not require production credentials",
)


@dataclass(frozen=True)
class FrontendE2EOptInResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[FrontendE2EOptInResult]:
    workflow_text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    results = [
        FrontendE2EOptInResult(str(WORKFLOW.relative_to(REPO_ROOT)), WORKFLOW.exists(), "workflow present" if WORKFLOW.exists() else "workflow missing"),
        FrontendE2EOptInResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing"),
    ]

    for snippet in WORKFLOW_SNIPPETS:
        results.append(
            FrontendE2EOptInResult(
                str(WORKFLOW.relative_to(REPO_ROOT)),
                snippet in workflow_text,
                f"contains {snippet!r}" if snippet in workflow_text else f"missing {snippet!r}",
            )
        )

    for snippet in DOC_SNIPPETS:
        results.append(
            FrontendE2EOptInResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend E2E opt-in workflow check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
