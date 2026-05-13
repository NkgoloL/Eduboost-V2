#!/usr/bin/env python3
"""Validate production-readiness item 20: final release-blocker checklist."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.final_release_blockers.production_readiness_contracts import default_final_release_blocker_readiness_report


REQUIRED_FILES = (
    "app/modules/final_release_blockers/__init__.py",
    "app/modules/final_release_blockers/production_readiness_contracts.py",
    "docs/adr/ADR-020-final-release-blocker-checklist.md",
    "docs/release_blockers/final_release_blocker_architecture_contract.md",
    "docs/release_blockers/final_release_blocker_register.md",
    "docs/release_blockers/release_blocker_domain_summary.md",
    "docs/release_blockers/release_blocker_waiver_policy.md",
    "docs/release_blockers/external_manual_dependency_register.md",
    "docs/release_blockers/final_go_no_go_checklist.md",
    "docs/release_blockers/final_release_blocker_closure_register.md",
    "docs/release_blockers/final_release_blocker_evidence_bundle.md",
    "docs/release_blockers/final_launch_boundary_statement.md",
    "docs/backlog/production_readiness/20_final_release-blocker_checklist.md",
    "tests/unit/test_final_release_blocker_checklist.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/final_release_blockers/production_readiness_contracts.py": (
        "class ReleaseBlockerDomain",
        "class BlockerSeverity",
        "class BlockerStatus",
        "class LaunchAuthority",
        "class FinalDecision",
        "FinalReleaseBlockerDecision",
        "ReleaseBlockerItem",
        "ReleaseBlockerDomainSummary",
        "ReleaseWaiverRule",
        "ExternalManualDependency",
        "FinalGoNoGoChecklist",
        "ReleaseBlockerClosureRecord",
        "compute_release_blocker_checksum",
        "summarize_blockers",
        "determine_final_decision",
        "validate_final_release_bundle",
        "default_final_release_blocker_readiness_report",
    ),
    "docs/adr/ADR-020-final-release-blocker-checklist.md": (
        "Final Release-Blocker Checklist",
        "final release-blocker checklist is required",
        "closure evidence is required",
        "release-blocker severity cannot be waived by default",
        "external/manual dependency boundary is required",
        "final go/no-go decision is required",
    ),
    "docs/release_blockers/final_release_blocker_architecture_contract.md": (
        "Final Release Blocker Architecture Contract",
        "release-blocker domain model",
        "release-blocker severity model",
        "launch authority model",
        "final go/no-go decision model",
        "Repository-side release-blocker evidence does not authorize production launch by itself",
    ),
    "docs/release_blockers/final_release_blocker_register.md": (
        "Final Release Blocker Register",
        "blocker ID must follow RB-### format",
        "closed blockers require closure evidence",
        "waived blockers require waiver evidence",
        "critical/release-blocker items cannot remain open",
    ),
    "docs/release_blockers/release_blocker_domain_summary.md": (
        "Release Blocker Domain Summary",
        "backend API",
        "POPIA consent",
        "testing quality",
        "operations support",
        "external/manual domain requires manual dependency",
    ),
    "docs/release_blockers/release_blocker_waiver_policy.md": (
        "Release Blocker Waiver Policy",
        "waiver expiry must be between 1 and 30 days",
        "waiver requires compensating controls",
        "release-blocker severity cannot be waived",
    ),
    "docs/release_blockers/external_manual_dependency_register.md": (
        "External Manual Dependency Register",
        "GitHub branch protection settings verified outside repository",
        "Legal/privacy launch approval completed outside repository",
        "required external dependencies must be closed before launch",
    ),
    "docs/release_blockers/final_go_no_go_checklist.md": (
        "Final Go/No-Go Checklist",
        "known issues reviewed",
        "rollback reviewed",
        "privacy/security reviewed",
        "release owner approval is required",
        "GO decision must include external/manual dependency review",
    ),
    "docs/release_blockers/final_launch_boundary_statement.md": (
        "Final Launch Boundary Statement",
        "does not approve production launch by itself",
        "GitHub repository settings and branch protection",
        "live cloud infrastructure state",
        "human release-owner signoff",
    ),
    "docs/backlog/production_readiness/20_final_release-blocker_checklist.md": (
        "20.6 Repository-side implementation evidence",
        "docs/release_blockers/final_release_blocker_architecture_contract.md",
        "scripts/check_final_release_blocker_checklist.py",
        "make final-release-blocker-checklist-check",
    ),
    "Makefile": (
        "final-release-blocker-checklist-check:",
        "scripts/check_final_release_blocker_checklist.py",
    ),
}


@dataclass(frozen=True)
class FinalReleaseBlockerResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[FinalReleaseBlockerResult]:
    results: list[FinalReleaseBlockerResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(FinalReleaseBlockerResult(rel_path, path.exists(), "file present" if path.exists() else "file missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                FinalReleaseBlockerResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_final_release_blocker_readiness_report()
        results.extend(
            [
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["decision_issues"] == [], "final blocker decision validates"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["domain_summary_issues"] == [], "domain summaries validate"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["release_blocker_issues"] == [], "release blockers validate"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["waiver_rule_issues"] == [], "waiver rules validate"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["external_dependency_issues"] == [], "external dependencies validate"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["final_checklist_issues"] == [], "final checklist validates"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["closure_record_issues"] == [], "closure records validate"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["final_bundle_issues"] == [], "final bundle validates"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["blocker_summary"].get("closed") == 3, "blocker summary sample passes"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", report["computed_decision"] == "go", "computed final decision sample passes"),
                FinalReleaseBlockerResult("final_release_blocker_contracts", len(str(report["checksum_sample"])) == 64, "release blocker checksum sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover
        results.append(FinalReleaseBlockerResult("final_release_blocker_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Final release blocker checklist check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
