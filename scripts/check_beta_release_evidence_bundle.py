#!/usr/bin/env python3
"""Validate beta release evidence bundle index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_release_evidence_bundle.md"
GENERATOR = REPO_ROOT / "scripts" / "generate_beta_release_evidence_bundle.py"

REQUIRED_SNIPPETS = (
    "Beta Release Evidence Bundle",
    "backend runtime/API",
    "release evidence manifest",
    "staging release gate",
    "deployment readiness",
    "project evidence index",
    "beta readiness contract",
    "staging smoke manifest",
    "beta sign-off manifest",
    "rollback runbook",
    "post-deploy smoke checklist",
    "Cluster C POPIA consent closure",
    "Cluster D closure",
    "Cluster E closure",
    "Cluster F closure",
    "Cluster G closure",
    "does not replace execution logs, approvals, or deployment platform records",
    "make beta-release-evidence-bundle",
)

GENERATOR_SNIPPETS = (
    "BUNDLE_ARTIFACTS",
    "RELEASE_CANDIDATE",
    "docs/frontend/CLUSTER_G_CLOSURE.md",
)


@dataclass(frozen=True)
class BetaReleaseBundleResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[BetaReleaseBundleResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    results = [
        BetaReleaseBundleResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "bundle present" if DOC.exists() else "bundle missing"),
        BetaReleaseBundleResult(str(GENERATOR.relative_to(REPO_ROOT)), GENERATOR.exists(), "generator present" if GENERATOR.exists() else "generator missing"),
    ]

    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaReleaseBundleResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in GENERATOR_SNIPPETS:
        results.append(
            BetaReleaseBundleResult(
                str(GENERATOR.relative_to(REPO_ROOT)),
                snippet in generator_text,
                f"contains {snippet!r}" if snippet in generator_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Beta release evidence bundle check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
