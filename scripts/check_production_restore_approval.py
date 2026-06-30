#!/usr/bin/env python3
"""Validate production restore approval guard evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "production_restore_approval.md"
RESTORE_SCRIPT = REPO_ROOT / "scripts" / "run_database_restore.py"

DOC_SNIPPETS = (
    "Production Restore Approval Guard",
    "backup artifact ID",
    "target environment",
    "approver",
    "approval ticket",
    "approval timestamp",
    "integrity status",
    "rollback plan",
    "production restore requires `--allow-production-target`",
)

SCRIPT_SNIPPETS = (
    "--allow-production-target",
    "validate_target_environment",
    "production restore requires --allow-production-target",
)


@dataclass(frozen=True)
class ProductionRestoreApprovalResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ProductionRestoreApprovalResult]:
    results: list[ProductionRestoreApprovalResult] = []
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    script_text = RESTORE_SCRIPT.read_text(encoding="utf-8") if RESTORE_SCRIPT.exists() else ""

    results.append(
        ProductionRestoreApprovalResult(
            str(DOC.relative_to(REPO_ROOT)),
            DOC.exists(),
            "approval doc present" if DOC.exists() else "approval doc missing",
        )
    )

    for snippet in DOC_SNIPPETS:
        results.append(
            ProductionRestoreApprovalResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in SCRIPT_SNIPPETS:
        results.append(
            ProductionRestoreApprovalResult(
                str(RESTORE_SCRIPT.relative_to(REPO_ROOT)),
                snippet in script_text,
                f"contains {snippet!r}" if snippet in script_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Production restore approval guard check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
