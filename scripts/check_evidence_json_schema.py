#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_KEYS = {"status", "captured_at", "required"}


def check(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path.relative_to(ROOT)} missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path.relative_to(ROOT)} invalid JSON: {exc}"]
    return [f"{path.relative_to(ROOT)} missing key {key}" for key in REQUIRED_KEYS if key not in data]


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: check_evidence_json_schema.py <json-file> [<json-file> ...]")
        return 2
    failures: list[str] = []
    for item in argv:
        failures.extend(check(ROOT / item))
    if failures:
        print("Evidence schema failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS evidence JSON schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
