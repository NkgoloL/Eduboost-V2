#!/usr/bin/env python3
"""Validate release artifact retention contract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_artifact_retention_contract.md"

REQUIRED_SNIPPETS = (
    "Release Artifact Retention Contract",
    "beta release evidence bundle",
    "beta sign-off manifest",
    "staging smoke evidence manifest",
    "release candidate tag manifest",
    "release approval workflow run",
    "Cluster H closure report",
    "post-deploy staging smoke checklist",
    "rollback runbook",
    "OpenAPI contract snapshot",
    "artifacts are committed or attached to CI workflow runs",
    "workflow logs are retained according to repository policy",
    "release candidate tag references the reviewed commit",
    "generated coverage output is not treated as release evidence",
    "local `coverage.xml`",
    "temporary patch directories",
    "make release-artifact-retention-contract-check",
)


@dataclass(frozen=True)
class ReleaseArtifactRetentionResult:
    ok: bool
    detail: str


def run_checks() -> list[ReleaseArtifactRetentionResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        ReleaseArtifactRetentionResult(DOC.exists(), "contract present" if DOC.exists() else "contract missing")
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            ReleaseArtifactRetentionResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Release artifact retention contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
