#!/usr/bin/env python3
"""Validate merge-control evidence gate."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "merge_control_evidence_gate.md"

REQUIRED_SNIPPETS = (
    "Merge-Control Evidence Gate",
    "final reviewer pack checklist is present",
    "final release evidence table of contents is present",
    "PR-ready final closure certificate is present",
    "final merge signoff lock is present",
    "release owner post-closeout decision record is present",
    "final evidence no-op execution assertion is present",
    "archival lock assertion is present",
    "release handoff freeze assertion is present",
    "final acceptance packet index is present",
    "final release evidence ledger is present",
    "Cluster H release readiness check is failing",
    "release candidate or commit SHA is inconsistent",
    "final evidence no-op execution assertion is missing",
    "unresolved blocker variance is present",
    "manual approval workflow reference is missing",
    "branch sync and rebase checklist is incomplete",
    "generated artifact conflict is unresolved",
    "PR-ready final closure certificate is missing",
    "archival lock assertion is missing",
    "post-closeout evidence access policy is missing",
    "merge-control gate must reference release candidate and commit SHA",
    "merge-control gate must preserve non-force-push branch discipline",
    "merge-control gate must preserve no-op execution boundary",
    "merge-control gate must preserve controlled staging/beta scope",
    "merge-control gate must not authorize unrestricted production launch",
    "does not approve production launch, execute deployment, create release tags, or merge the pull request automatically",
    "make merge-control-evidence-gate-check",
)


@dataclass(frozen=True)
class MergeControlEvidenceGateResult:
    ok: bool
    detail: str


def run_checks() -> list[MergeControlEvidenceGateResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [MergeControlEvidenceGateResult(DOC.exists(), "gate present" if DOC.exists() else "gate missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            MergeControlEvidenceGateResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Merge-control evidence gate check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
