#!/usr/bin/env python3
"""Validate previously captured pytest release evidence files."""
from __future__ import annotations

import re
from pathlib import Path


REQUIRED_EVIDENCE = [
    Path("docs/release/unit_latest_green.txt"),
    Path("docs/release/integration_latest_green.txt"),
    Path("docs/release/full_pytest_latest_green.txt"),
]


def _file_is_green(path: Path) -> bool:
    if not path.exists():
        print(f"- FAIL [file] {path}: missing")
        return False

    text = path.read_text(encoding="utf-8")
    checks = {
        "return_code_zero": "# Return code: 0" in text,
        "passed_summary": re.search(r"\b\d+\s+passed\b", text) is not None,
        "no_failed_summary": " failed" not in text and " errors" not in text and "FAILED " not in text,
        "command_recorded": "# Command:" in text,
        "timestamp_recorded": "# Captured at:" in text,
    }

    ok = all(checks.values())
    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"- {status} [content] {path}: {name}")

    return ok


def main() -> int:
    print("Pytest release evidence check")
    ok = all(_file_is_green(path) for path in REQUIRED_EVIDENCE)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
