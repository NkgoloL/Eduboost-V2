#!/usr/bin/env python3
"""Validate production-readiness item 14: testing, release evidence, and quality gates."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.quality_gates.production_readiness_contracts import default_quality_gate_readiness_report


REQUIRED_FILES = (
    "app/modules/quality_gates/__init__.py",
    "app/modules/quality_gates/production_readiness_contracts.py",
    "docs/adr/ADR-014-testing-release-evidence-quality-gates.md",
    "docs/testing/testing_release_evidence_architecture_contract.md",
    "docs/testing/test_strategy_matrix_contract.md",
    "docs/testing/coverage_quality_threshold_contract.md",
    "docs/testing/quality_gate_waiver_policy.md",
    "docs/testing/release_evidence_bundle_contract.md",
    "docs/testing/defect_triage_release_blocker_contract.md",
    "docs/testing/beta_release_quality_gate_checklist.md",
    "docs/testing/production_release_quality_gate_checklist.md",
    "docs/testing/known_issues_release_register.md",
    "docs/backlog/production_readiness/14_testing_release_evidence_and_quality_gates.md",
    "tests/unit/test_testing_release_quality_gates_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/quality_gates/production_readiness_contracts.py": (
        "class TestLayer",
        "class QualityGateStatus",
        "class ReleaseStage",
        "class DefectSeverity",
        "class EvidenceType",
        "TestingStrategyDecision",
        "TestSuiteContract",
        "CoverageThreshold",
        "QualityGate",
        "ReleaseEvidenceItem",
        "DefectTriageRule",
        "ReleaseChecklist",
        "compute_evidence_checksum",
        "validate_evidence_bundle",
        "summarize_gate_status",
        "default_quality_gate_readiness_report",
    ),
    "docs/adr/ADR-014-testing-release-evidence-quality-gates.md": (
        "Testing, Release Evidence, and Quality Gates Decision",
        "layered automated testing",
        "release evidence bundles",
        "manual approval is required for beta and production",
        "release blockers must block production",
        "known issues review is required",
    ),
    "docs/testing/testing_release_evidence_architecture_contract.md": (
        "Testing Release Evidence Architecture Contract",
        "unit tests",
        "integration tests",
        "API contract tests",
        "E2E tests",
        "security tests",
        "accessibility tests",
        "performance tests",
        "release approval",
        "known issues register",
    ),
    "docs/testing/test_strategy_matrix_contract.md": (
        "Test Strategy Matrix Contract",
        "test layer",
        "command",
        "required for pull request",
        "required for production",
        "pull request tests must be deterministic",
        "OpenAPI contract tests must detect drift",
    ),
    "docs/testing/coverage_quality_threshold_contract.md": (
        "Coverage Quality Threshold Contract",
        "minimum line coverage",
        "minimum branch coverage",
        "coverage ratchet",
        "production line coverage threshold must be at least 70 percent",
        "coverage report must be retained as release evidence",
    ),
    "docs/testing/quality_gate_waiver_policy.md": (
        "Quality Gate Waiver Policy",
        "release blockers cannot be waived for production",
        "security scan failures require security-owner review",
        "waiver must include owner, expiry, affected release stage, and evidence link",
    ),
    "docs/testing/release_evidence_bundle_contract.md": (
        "Release Evidence Bundle Contract",
        "test report",
        "coverage report",
        "security scan",
        "OpenAPI artifact",
        "smoke test report",
        "checksum SHA-256",
    ),
    "docs/testing/defect_triage_release_blocker_contract.md": (
        "Defect Triage and Release Blocker Contract",
        "release blockers block production",
        "release blockers allowed for production must be zero",
        "defects require fix or waiver",
        "known issues register must be reviewed before beta and production",
    ),
    "docs/backlog/production_readiness/14_testing_release_evidence_and_quality_gates.md": (
        "14.6 Repository-side implementation evidence",
        "docs/testing/testing_release_evidence_architecture_contract.md",
        "scripts/check_testing_release_quality_gates_production_readiness.py",
        "make testing-release-quality-gates-production-readiness-check",
    ),
    "Makefile": (
        "testing-release-quality-gates-production-readiness-check:",
        "scripts/check_testing_release_quality_gates_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class QualityGateReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[QualityGateReadinessResult]:
    results: list[QualityGateReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            QualityGateReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                QualityGateReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_quality_gate_readiness_report()
        results.extend(
            [
                QualityGateReadinessResult("quality_gate_contracts", report["strategy_issues"] == [], "testing strategy validates"),
                QualityGateReadinessResult("quality_gate_contracts", report["test_suite_issues"] == [], "test suite contracts validate"),
                QualityGateReadinessResult("quality_gate_contracts", report["coverage_threshold_issues"] == [], "coverage thresholds validate"),
                QualityGateReadinessResult("quality_gate_contracts", report["quality_gate_issues"] == [], "quality gates validate"),
                QualityGateReadinessResult("quality_gate_contracts", report["release_evidence_issues"] == [], "release evidence items validate"),
                QualityGateReadinessResult("quality_gate_contracts", report["evidence_bundle_issues"] == [], "release evidence bundle validates"),
                QualityGateReadinessResult("quality_gate_contracts", report["defect_triage_issues"] == [], "defect triage validates"),
                QualityGateReadinessResult("quality_gate_contracts", report["release_checklist_issues"] == [], "release checklists validate"),
                QualityGateReadinessResult("quality_gate_contracts", len(str(report["checksum_sample"])) == 64, "evidence checksum sample passes"),
                QualityGateReadinessResult("quality_gate_contracts", report["gate_status_sample"] == "pass", "gate status summary sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover - defensive CLI output
        results.append(QualityGateReadinessResult("quality_gate_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Testing release quality gates production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
