#!/usr/bin/env python3
"""Check that the consolidated core CI lane exists and calls Makefile targets."""
from __future__ import annotations

from pathlib import Path


REQUIRED_FILES = [
    Path(".github/workflows/ci-core.yml"),
    Path("docs/release/ci_workflow_consolidation.md"),
    Path("docs/release/route_alias_policy.md"),
    Path("scripts/check_route_alias_matrix.py"),
]

REQUIRED_CONTENT = {
    Path(".github/workflows/ci-core.yml"): [
        "name: CI Core",
        "make release-hygiene-check",
        "make route-alias-policy-check",
        "pytest -c pytest.ini tests/unit -q --no-cov",
        "pytest -c pytest.ini tests/integration -q --no-cov",
    ],
    Path("docs/release/ci_workflow_consolidation.md"): [
        "Primary CI lanes",
        "make ci-core-local",
        "docs/release/ci_evidence.md",
    ],
    Path("docs/release/route_alias_policy.md"): [
        "/api/v2",
        "/v2",
        "docs/release/route_alias_exceptions.txt",
    ],
}


def main() -> int:
    failures: list[str] = []
    print("CI workflow consolidation check")

    for path in REQUIRED_FILES:
        if path.exists():
            print(f"- PASS [file] {path}: present")
        else:
            print(f"- FAIL [file] {path}: missing")
            failures.append(f"missing file {path}")

    for path, needles in REQUIRED_CONTENT.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for needle in needles:
            if needle in text:
                print(f"- PASS [content] {path}: contains {needle!r}")
            else:
                print(f"- FAIL [content] {path}: missing {needle!r}")
                failures.append(f"{path} missing {needle!r}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
