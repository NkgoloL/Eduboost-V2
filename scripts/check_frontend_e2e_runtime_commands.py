#!/usr/bin/env python3
"""Validate frontend E2E runtime command evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = REPO_ROOT / "Makefile"
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_e2e_runtime_commands.md"

MAKEFILE_SNIPPETS = (
    "frontend-e2e:",
    "frontend-e2e-smoke:",
    "frontend-e2e-mocked:",
    "PLAYWRIGHT_MOCK_API=1",
    "learner-mocked-api-journey.spec.ts",
    "parent-mocked-api-journey.spec.ts",
)

DOC_SNIPPETS = (
    "Frontend E2E Runtime Commands",
    "make frontend-e2e-smoke",
    "make frontend-e2e-mocked",
    "make frontend-e2e",
    "must not require production credentials",
    "learner-mocked-api-journey.spec.ts",
    "parent-mocked-api-journey.spec.ts",
)


@dataclass(frozen=True)
class FrontendE2ERuntimeCommandResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[FrontendE2ERuntimeCommandResult]:
    make_text = MAKEFILE.read_text(encoding="utf-8") if MAKEFILE.exists() else ""
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    results = [
        FrontendE2ERuntimeCommandResult("Makefile", MAKEFILE.exists(), "Makefile present" if MAKEFILE.exists() else "Makefile missing"),
        FrontendE2ERuntimeCommandResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing"),
    ]

    for snippet in MAKEFILE_SNIPPETS:
        results.append(
            FrontendE2ERuntimeCommandResult(
                "Makefile",
                snippet in make_text,
                f"contains {snippet!r}" if snippet in make_text else f"missing {snippet!r}",
            )
        )

    for snippet in DOC_SNIPPETS:
        results.append(
            FrontendE2ERuntimeCommandResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Frontend E2E runtime command check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
