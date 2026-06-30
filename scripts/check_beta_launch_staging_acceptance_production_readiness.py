#!/usr/bin/env python3
"""Validate production-readiness item 18: beta launch, staging acceptance, and product scope."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.beta_launch.production_readiness_contracts import default_beta_launch_readiness_report


REQUIRED_FILES = (
    "app/modules/beta_launch/__init__.py",
    "app/modules/beta_launch/production_readiness_contracts.py",
    "docs/adr/ADR-018-beta-launch-staging-acceptance-product-scope.md",
    "docs/beta_launch/beta_launch_staging_acceptance_architecture_contract.md",
    "docs/beta_launch/beta_product_scope_contract.md",
    "docs/beta_launch/staging_acceptance_criteria_contract.md",
    "docs/beta_launch/beta_entry_exit_criteria_contract.md",
    "docs/beta_launch/beta_cohort_rollout_contract.md",
    "docs/beta_launch/beta_feedback_intake_contract.md",
    "docs/beta_launch/beta_known_issues_register.md",
    "docs/beta_launch/beta_launch_readiness_review.md",
    "docs/beta_launch/post_beta_review_contract.md",
    "docs/backlog/production_readiness/18_beta_launch_staging_acceptance_and_product_scope.md",
    "tests/unit/test_beta_launch_staging_acceptance_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/beta_launch/production_readiness_contracts.py": (
        "class BetaStage",
        "class LaunchDecision",
        "class ProductScopeArea",
        "class AcceptanceStatus",
        "class FeedbackSeverity",
        "BetaLaunchDecision",
        "ProductScopeItem",
        "StagingAcceptanceCriterion",
        "BetaEntryCriterion",
        "BetaExitCriterion",
        "BetaCohortPlan",
        "FeedbackIntakeRule",
        "KnownIssue",
        "LaunchReadinessReview",
        "compute_beta_launch_checksum",
        "summarize_acceptance_status",
        "validate_beta_launch_bundle",
        "default_beta_launch_readiness_report",
    ),
    "docs/adr/ADR-018-beta-launch-staging-acceptance-product-scope.md": (
        "Beta Launch, Staging Acceptance, and Product Scope",
        "beta product scope is required",
        "staging acceptance criteria are required",
        "controlled cohort limits are required",
        "known issues review is required",
        "no-go authority is required",
    ),
    "docs/beta_launch/beta_launch_staging_acceptance_architecture_contract.md": (
        "Beta Launch Staging Acceptance Architecture Contract",
        "beta product scope",
        "explicit exclusions",
        "staging acceptance criteria",
        "controlled cohort plan",
        "known issues register",
        "no-go authority",
    ),
    "docs/beta_launch/beta_product_scope_contract.md": (
        "Beta Product Scope Contract",
        "learner onboarding",
        "diagnostics",
        "lesson generation with AI safety controls",
        "billing is disabled for beta launch",
        "production launch is not approved by this evidence",
    ),
    "docs/beta_launch/staging_acceptance_criteria_contract.md": (
        "Staging Acceptance Criteria Contract",
        "backend API smoke evidence",
        "frontend journey smoke evidence",
        "privacy and consent evidence",
        "failed blocking criteria block beta launch",
        "waived criteria require waiver path",
    ),
    "docs/beta_launch/beta_entry_exit_criteria_contract.md": (
        "Beta Entry and Exit Criteria Contract",
        "repository evidence checks pass",
        "known issues register reviewed",
        "critical beta defects remain zero",
        "support response SLA met",
        "exit criteria require threshold",
    ),
    "docs/beta_launch/beta_cohort_rollout_contract.md": (
        "Beta Cohort Rollout Contract",
        "max learners",
        "max guardians",
        "allowed grades",
        "beta cohort requires consent",
        "beta cohort requires rollback support",
    ),
    "docs/beta_launch/beta_feedback_intake_contract.md": (
        "Beta Feedback Intake Contract",
        "in-app feedback",
        "support email",
        "high feedback requires escalation",
        "critical feedback requires escalation",
    ),
    "docs/beta_launch/beta_known_issues_register.md": (
        "Beta Known Issues Register",
        "high and critical known issues must block beta or be explicitly accepted",
        "accepted beta known issue requires workaround",
    ),
    "docs/beta_launch/beta_launch_readiness_review.md": (
        "Beta Launch Readiness Review",
        "launch decision",
        "reviewed staging acceptance",
        "general availability requires separate production launch approval",
    ),
    "docs/backlog/production_readiness/18_beta_launch_staging_acceptance_and_product_scope.md": (
        "18.6 Repository-side implementation evidence",
        "docs/beta_launch/beta_launch_staging_acceptance_architecture_contract.md",
        "scripts/check_beta_launch_staging_acceptance_production_readiness.py",
        "make beta-launch-staging-acceptance-production-readiness-check",
    ),
    "Makefile": (
        "beta-launch-staging-acceptance-production-readiness-check:",
        "scripts/check_beta_launch_staging_acceptance_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class BetaLaunchReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[BetaLaunchReadinessResult]:
    results: list[BetaLaunchReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            BetaLaunchReadinessResult(rel_path, path.exists(), "file present" if path.exists() else "file missing")
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                BetaLaunchReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_beta_launch_readiness_report()
        results.extend(
            [
                BetaLaunchReadinessResult("beta_launch_contracts", report["decision_issues"] == [], "beta launch decision validates"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["product_scope_issues"] == [], "product scope validates"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["staging_acceptance_issues"] == [], "staging acceptance validates"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["entry_criteria_issues"] == [], "entry criteria validate"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["exit_criteria_issues"] == [], "exit criteria validate"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["cohort_issues"] == [], "cohort plan validates"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["feedback_rule_issues"] == [], "feedback rules validate"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["known_issue_issues"] == [], "known issues validate"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["review_issues"] == [], "launch readiness review validates"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["launch_bundle_issues"] == [], "beta launch bundle validates"),
                BetaLaunchReadinessResult("beta_launch_contracts", report["acceptance_status_sample"] == "pass", "acceptance status sample passes"),
                BetaLaunchReadinessResult("beta_launch_contracts", len(str(report["checksum_sample"])) == 64, "beta launch checksum sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover
        results.append(BetaLaunchReadinessResult("beta_launch_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Beta launch staging acceptance production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
