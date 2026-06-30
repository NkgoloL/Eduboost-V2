#!/usr/bin/env python3
"""Validate database resilience environment-variable matrix."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "database_resilience_env_matrix.md"

REQUIRED_SNIPPETS = (
    "Database Resilience Environment Matrix",
    "DATABASE_URL",
    "BACKUP_ENCRYPTION_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_STORAGE_CONTAINER",
    "production restore requires explicit approval",
    "CI must use dry-run backup and restore commands",
    "restore evidence must record learner, consent, and audit count status",
)


@dataclass(frozen=True)
class EnvMatrixResult:
    ok: bool
    detail: str


def run_checks() -> list[EnvMatrixResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [EnvMatrixResult(DOC.exists(), "matrix present" if DOC.exists() else "matrix missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            EnvMatrixResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Database resilience environment matrix check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
