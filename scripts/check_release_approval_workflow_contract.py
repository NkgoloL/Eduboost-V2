#!/usr/bin/env python3
"""Validate release approval workflow contract evidence."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "release_approval_workflow_contract.md"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "beta-release-approval.yml"

DOC_SNIPPETS = (
    "Release Approval Workflow Contract",
    "release candidate identifier",
    "target environment",
    "commit SHA",
    "beta release evidence bundle",
    "beta sign-off manifest",
    "staging smoke evidence manifest",
    "rollback runbook",
    "post-deploy smoke checklist",
    "manual workflow dispatch",
    "approver identity from platform audit trail",
    "make release-approval-workflow-contract-check",
)

WORKFLOW_SNIPPETS = (
    "workflow_dispatch:",
    "release_candidate",
    "target_environment",
    "rollback_owner",
    "post_deploy_owner",
    "RELEASE_CANDIDATE",
    "TARGET_ENVIRONMENT",
    "ROLLBACK_OWNER",
    "POST_DEPLOY_OWNER",
    "make beta-release-evidence-bundle",
    "make cluster-h-release-readiness-check",
)


@dataclass(frozen=True)
class ReleaseApprovalWorkflowResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[ReleaseApprovalWorkflowResult]:
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    workflow_text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""
    results = [
        ReleaseApprovalWorkflowResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "contract present" if DOC.exists() else "contract missing"),
        ReleaseApprovalWorkflowResult(str(WORKFLOW.relative_to(REPO_ROOT)), WORKFLOW.exists(), "workflow present" if WORKFLOW.exists() else "workflow missing"),
    ]

    for snippet in DOC_SNIPPETS:
        results.append(
            ReleaseApprovalWorkflowResult(
                str(DOC.relative_to(REPO_ROOT)),
                snippet in doc_text,
                f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}",
            )
        )

    for snippet in WORKFLOW_SNIPPETS:
        results.append(
            ReleaseApprovalWorkflowResult(
                str(WORKFLOW.relative_to(REPO_ROOT)),
                snippet in workflow_text,
                f"contains {snippet!r}" if snippet in workflow_text else f"missing {snippet!r}",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Release approval workflow contract check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
