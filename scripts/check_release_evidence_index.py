#!/usr/bin/env python3
"""Check release evidence index and route alias documentation exist."""
from __future__ import annotations

from pathlib import Path


REQUIRED_FILES = [
    Path("docs/release/EVIDENCE_INDEX.md"),
    Path("docs/release/test_environment_contract.md"),
    Path("scripts/check_test_environment.py"),
    Path("scripts/generate_route_alias_matrix.py"),
]

REQUIRED_CONTENT = {
    Path("docs/release/EVIDENCE_INDEX.md"): [
        "Full repository pytest discovery is green locally",
        "CI run is green on protected branch",
        "Staging deployment smoke test passed",
        "Legal/POPIA review complete",
        "Security review complete",
    ],
    Path("docs/release/test_environment_contract.md"): [
        "DATABASE_URL",
        "ENCRYPTION_KEY",
        "ALLOWED_ORIGINS",
        "make test-env-check",
    ],
}


def main() -> int:
    failures: list[str] = []

    print("Release evidence index check")
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
