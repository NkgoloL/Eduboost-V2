#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {
    Path("docs/release/health_readiness_diagnostic_contract.md"): [
        "Lightweight health",
        "Deep health",
        "database connectivity",
        "Alembic current revision",
        "required core table presence",
        "no unsafe public write operations",
    ],
    Path("docs/release/schema_drift_evidence_contract.md"): [
        "make schema-drift-check",
        "make schema-drift-check-db",
        "alembic upgrade head",
        "alembic stamp head",
    ],
}

HEALTH_SOURCE_PATTERNS = [
    Path("app/api_v2_routers/health.py"),
    Path("app/api/health.py"),
    Path("app/routes/health.py"),
]


def _existing_health_sources() -> list[Path]:
    return [path for path in HEALTH_SOURCE_PATTERNS if path.exists()]


def _source_has_unsafe_write(text: str) -> bool:
    unsafe_patterns = [
        r"\.commit\(",
        r"\.delete\(",
        r"\.add\(",
        r"INSERT\s+INTO",
        r"UPDATE\s+",
        r"DELETE\s+FROM",
    ]
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in unsafe_patterns)


def main() -> int:
    failures: list[str] = []
    print("Health/readiness diagnostic contract check")

    for path, needles in CONTRACTS.items():
        if not path.exists():
            print(f"- FAIL [file] {path}: missing")
            failures.append(f"missing {path}")
            continue

        text = path.read_text(encoding="utf-8")
        print(f"- PASS [file] {path}: present")
        for needle in needles:
            if needle in text:
                print(f"- PASS [content] {path}: contains {needle!r}")
            else:
                print(f"- FAIL [content] {path}: missing {needle!r}")
                failures.append(f"{path} missing {needle!r}")

    health_sources = _existing_health_sources()
    if not health_sources:
        print("- WARN [source] no known health router source found")
    for path in health_sources:
        text = path.read_text(encoding="utf-8")
        if _source_has_unsafe_write(text):
            print(f"- FAIL [source] {path}: health source appears to perform write-like DB operations")
            failures.append(f"{path} unsafe write-like operation")
        else:
            print(f"- PASS [source] {path}: no obvious write-like DB operation detected")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS health/readiness diagnostics documented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
