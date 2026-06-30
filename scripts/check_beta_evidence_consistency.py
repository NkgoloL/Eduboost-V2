#!/usr/bin/env python3
"""Validate beta release evidence consistency."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

DOC = REPO_ROOT / "docs" / "operations" / "beta_evidence_consistency_guard.md"

DOCUMENTS = (
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/beta_release_final_checklist.md",
    "docs/operations/beta_release_execution_plan.md",
    "docs/operations/beta_release_pr_body.md",
    "docs/operations/final_release_verification_bundle.md",
    "docs/operations/project_release_closure_index.md",
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/operations/pr_closeout_evidence_checklist.md",
)

REQUIRED_REFERENCES = (
    "docs/operations/CLUSTER_H_CLOSURE.md",
    "docs/operations/beta_release_evidence_bundle.md",
    "docs/operations/project_release_closure_index.md",
    "docs/operations/final_release_verification_bundle.md",
)

REQUIRED_COMMANDS = (
    "make final-release-verification",
    "make cluster-h-release-readiness-check",
    "make cluster-h-closure-check",
)

REQUIRED_BOUNDARY_PHRASES = (
    "does not authorize unrestricted production launch",
    "controlled staging/beta",
)


@dataclass(frozen=True)
class BetaEvidenceConsistencyResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[BetaEvidenceConsistencyResult]:
    results: list[BetaEvidenceConsistencyResult] = []
    guard_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""

    results.append(
        BetaEvidenceConsistencyResult(
            "file",
            str(DOC.relative_to(REPO_ROOT)),
            DOC.exists(),
            "guard present" if DOC.exists() else "guard missing",
        )
    )

    for snippet in (
        "Beta Evidence Consistency Guard",
        "Required Shared References",
        "Required Shared Commands",
        "Required Shared Boundary",
        "make beta-evidence-consistency-check",
    ):
        results.append(
            BetaEvidenceConsistencyResult(
                "guard",
                str(DOC.relative_to(REPO_ROOT)),
                snippet in guard_text,
                f"contains {snippet!r}" if snippet in guard_text else f"missing {snippet!r}",
            )
        )

    for rel_path in DOCUMENTS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        results.append(
            BetaEvidenceConsistencyResult(
                "file",
                rel_path,
                path.exists(),
                "present" if path.exists() else "missing",
            )
        )

        if rel_path in (
            "docs/operations/beta_release_pr_body.md",
            "docs/operations/project_release_closure_index.md",
            "docs/operations/CLUSTER_H_CLOSURE.md",
        ):
            for ref in REQUIRED_REFERENCES:
                results.append(
                    BetaEvidenceConsistencyResult(
                        "reference",
                        rel_path,
                        ref in text,
                        f"contains {ref!r}" if ref in text else f"missing {ref!r}",
                    )
                )

        if rel_path in (
            "docs/operations/beta_release_pr_body.md",
            "docs/operations/final_release_verification_bundle.md",
            "docs/operations/pr_closeout_evidence_checklist.md",
        ):
            for command in REQUIRED_COMMANDS:
                results.append(
                    BetaEvidenceConsistencyResult(
                        "command",
                        rel_path,
                        command in text,
                        f"contains {command!r}" if command in text else f"missing {command!r}",
                    )
                )

        if rel_path in (
            "docs/operations/beta_release_pr_body.md",
            "docs/operations/beta_release_final_checklist.md",
            "docs/operations/CLUSTER_H_CLOSURE.md",
        ):
            for phrase in REQUIRED_BOUNDARY_PHRASES:
                results.append(
                    BetaEvidenceConsistencyResult(
                        "boundary",
                        rel_path,
                        phrase in text,
                        f"contains {phrase!r}" if phrase in text else f"missing {phrase!r}",
                    )
                )

    return results


def main() -> int:
    results = run_checks()
    print("Beta evidence consistency check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
