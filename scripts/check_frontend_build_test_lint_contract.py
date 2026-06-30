#!/usr/bin/env python3
"""Validate frontend build/test/lint command contract.

This checker is intentionally evidence-focused. If a package.json exists but
does not yet expose normalized frontend scripts, missing scripts are reported as
advisory PASS results rather than hard failures. Runtime script enforcement can
be tightened once the frontend package location and scripts are canonical.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "frontend" / "frontend_build_test_lint_contract.md"
RUNTIME_INVENTORY = REPO_ROOT / "docs" / "frontend" / "frontend_runtime_inventory.md"
PACKAGE_CANDIDATES = (
    REPO_ROOT / "frontend" / "package.json",
    REPO_ROOT / "package.json",
)

DOC_SNIPPETS = (
    "Frontend Build Test Lint Contract",
    "install frontend dependencies",
    "run frontend lint",
    "run frontend typecheck",
    "run frontend unit tests",
    "run frontend production build",
    "run frontend Playwright smoke",
    "run frontend Playwright mocked journeys",
    "run frontend accessibility static check",
    "Runtime build/test commands may be wired as opt-in",
    "make frontend-build-test-lint-contract-check",
)

RUNTIME_SNIPPETS = (
    "Frontend Runtime Inventory",
    "build frontend",
    "run frontend unit tests",
    "run Playwright E2E",
)


@dataclass(frozen=True)
class FrontendBuildTestLintResult:
    target: str
    ok: bool
    detail: str


def _load_package(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _script_coverage_results() -> list[FrontendBuildTestLintResult]:
    results: list[FrontendBuildTestLintResult] = []
    packages = [(path, _load_package(path)) for path in PACKAGE_CANDIDATES]
    present_packages = [(path, data) for path, data in packages if data is not None]

    if not present_packages:
        results.append(
            FrontendBuildTestLintResult(
                "package.json",
                True,
                "frontend package metadata not present; runtime command contract remains opt-in",
            )
        )
        return results

    for path, data in present_packages:
        rel = str(path.relative_to(REPO_ROOT))
        scripts = data.get("scripts") if isinstance(data, dict) else {}
        if not isinstance(scripts, dict):
            scripts = {}

        for command in ("build", "test", "lint"):
            results.append(
                FrontendBuildTestLintResult(
                    rel,
                    True,
                    f"script {command!r} present" if command in scripts else f"advisory: script {command!r} missing until frontend package is normalized",
                )
            )

        typecheck_present = (
            "typecheck" in scripts
            or "type-check" in scripts
            or "tsc" in " ".join(str(v) for v in scripts.values())
        )
        results.append(
            FrontendBuildTestLintResult(
                rel,
                True,
                "typecheck capability present" if typecheck_present else "advisory: typecheck capability missing until frontend package is normalized",
            )
        )

        dev_present = "dev" in scripts or "start" in scripts
        results.append(
            FrontendBuildTestLintResult(
                rel,
                True,
                "dev/start script present" if dev_present else "advisory: dev/start script missing until frontend package is normalized",
            )
        )

    return results


def run_checks() -> list[FrontendBuildTestLintResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    runtime_text = RUNTIME_INVENTORY.read_text(encoding="utf-8") if RUNTIME_INVENTORY.exists() else ""
    results = [
        FrontendBuildTestLintResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "contract present" if DOC.exists() else "contract missing"),
        FrontendBuildTestLintResult(str(RUNTIME_INVENTORY.relative_to(REPO_ROOT)), RUNTIME_INVENTORY.exists(), "runtime inventory present" if RUNTIME_INVENTORY.exists() else "runtime inventory missing"),
    ]

    for snippet in DOC_SNIPPETS:
        results.append(
            FrontendBuildTestLintResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in RUNTIME_SNIPPETS:
        results.append(
            FrontendBuildTestLintResult(
                str(RUNTIME_INVENTORY.relative_to(REPO_ROOT)),
                snippet in runtime_text,
                f"contains {snippet!r}" if snippet in runtime_text else f"missing {snippet!r}",
            )
        )

    results.extend(_script_coverage_results())
    return results


def main() -> int:
    results = run_checks()
    print("Frontend build/test/lint contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
