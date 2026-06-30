#!/usr/bin/env python3
"""Validate release state snapshot evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_state_snapshot.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_release_state_snapshot.py"

REQUIRED_SNIPPETS = (
    "Release State Snapshot",
    "generated_at_utc",
    "branch:",
    "commit:",
    "release_candidate:",
    "Working Tree Status",
    "State Artifacts",
    "docs/operations/beta_release_readiness_contract.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "audits/reports/PR_INTEGRATION_SUMMARY.md",
    "docs/project_status.md",
    "does not replace CI logs, platform approvals, or release tag history",
    "make release-state-snapshot",
)

GENERATOR_SNIPPETS = (
    "generate_release_state_snapshot",
    "STATE_ARTIFACTS",
    "git",
    "status",
)


@dataclass(frozen=True)
class ReleaseStateSnapshotResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ReleaseStateSnapshotResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    results = [
        ReleaseStateSnapshotResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "snapshot present" if DOC.exists() else "snapshot missing"),
        ReleaseStateSnapshotResult(str(GENERATOR.relative_to(REPO_ROOT)), GENERATOR.exists(), "generator present" if GENERATOR.exists() else "generator missing"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseStateSnapshotResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in GENERATOR_SNIPPETS:
        results.append(
            ReleaseStateSnapshotResult(
                str(GENERATOR.relative_to(REPO_ROOT)),
                snippet in generator_text,
                f"contains {snippet!r}" if snippet in generator_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Release state snapshot check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
