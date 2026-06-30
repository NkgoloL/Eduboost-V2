#!/usr/bin/env python3
"""Validate final evidence no-op execution assertion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "final_evidence_noop_execution_assertion.md"

REQUIRED_SNIPPETS = (
    "Final Evidence No-Op Execution Assertion",
    "evidence checks do not deploy code",
    "evidence checks do not create release tags",
    "evidence checks do not approve production launch",
    "evidence checks do not modify production data",
    "evidence checks do not collect live learner data",
    "evidence checks do not bypass manual approvals",
    "evidence checks do not replace platform workflow logs",
    "evidence checks do not resolve blocker issues automatically",
    "evidence checks do not execute rollback automatically",
    "evidence checks do not contact beta participants automatically",
    "docs/operations/release_owner_execution_guardrail.md",
    "docs/operations/final_project_closeout_attestation.md",
    "docs/operations/final_merge_signoff_lock.md",
    "docs/operations/release_owner_post_closeout_decision_record.md",
    "docs/operations/final_release_handoff_package.md",
    "docs/operations/post_terminal_audit_readiness_assertion.md",
    "docs/operations/cluster_h_release_evidence_checksum_index.md",
    "no-op assertion must remain controlled staging/beta evidence",
    "no-op assertion must reference release candidate and commit SHA",
    "no-op assertion must preserve manual approval workflow references",
    "no-op assertion must preserve release owner accountability references",
    "no-op assertion must preserve audit readiness references",
    "no-op assertion must preserve source control history references",
    "does not approve production launch, execute deployment, create release tags, or replace manual approval",
    "make final-evidence-noop-execution-assertion-check",
)


@dataclass(frozen=True)
class FinalEvidenceNoopExecutionAssertionResult:
    ok: bool
    detail: str


def run_checks() -> list[FinalEvidenceNoopExecutionAssertionResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [FinalEvidenceNoopExecutionAssertionResult(DOC.exists(), "assertion present" if DOC.exists() else "assertion missing")]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            FinalEvidenceNoopExecutionAssertionResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Final evidence no-op execution assertion check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
