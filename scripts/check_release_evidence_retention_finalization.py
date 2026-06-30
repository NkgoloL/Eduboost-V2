#!/usr/bin/env python3
"""Validate release evidence retention finalization."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_evidence_retention_finalization.md"

REQUIRED_SNIPPETS = (
    "Release Evidence Retention Finalization",
    "final release evidence table of contents",
    "final acceptance packet index",
    "archival lock assertion",
    "post-closeout evidence access policy",
    "final release evidence ledger",
    "Cluster H release evidence checksum index",
    "evidence archive completeness guard",
    "post-beta evidence archive manifest",
    "final project closeout attestation",
    "PR-ready final closure certificate",
    "retention must reference release candidate and commit SHA",
    "retention must preserve final acceptance packet index",
    "retention must preserve final release evidence table of contents",
    "retention must preserve archival lock assertion",
    "retention must preserve no-op execution boundary",
    "retention must preserve post-closeout evidence access policy",
    "retention must preserve checksum and ledger references",
    "retention must avoid unnecessary learner personal information",
    "retention must remain controlled staging/beta evidence",
    "do not delete audit evidence",
    "do not rewrite source control history",
    "do not remove unresolved blocker variance records",
    "do not remove release-owner decision references",
    "do not remove manual approval workflow references",
    "do not use retention evidence as production launch authorization",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make release-evidence-retention-finalization-check",
)


@dataclass(frozen=True)
class ReleaseEvidenceRetentionFinalizationResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseEvidenceRetentionFinalizationResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [ReleaseEvidenceRetentionFinalizationResult(DOC.exists(), "finalization present" if DOC.exists() else "finalization missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseEvidenceRetentionFinalizationResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Release evidence retention finalization check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
