#!/usr/bin/env python3
"""Validate database restore-drill documentation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "database_restore_drill.md"

REQUIRED_SNIPPETS = (
    "Database Restore Drill",
    "backup artifact is encrypted",
    "restore target is non-production",
    "Verify learner record counts",
    "Verify consent record counts",
    "Verify audit event counts",
    "make runtime-check",
    "make popia-consent-closure-check",
    "make cluster-d-closure-check",
    "backup artifact ID",
)


@dataclass(frozen=True)
class RestoreDrillResult:
    ok: bool
    detail: str


def run_checks() -> list[RestoreDrillResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    return [
        RestoreDrillResult(
            ok=snippet in text,
            detail=f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
        )
        for snippet in REQUIRED_SNIPPETS
    ]


def main() -> int:
    results = run_checks()
    print("Database restore drill documentation check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
