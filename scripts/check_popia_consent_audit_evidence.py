#!/usr/bin/env python3
"""Aggregate evidence checker for Cluster C POPIA consent/audit baseline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = (
    "tests/unit/test_popia_ci_closure_contract.py",
    "tests/unit/test_consent_rejection_audit_check.py",
    "tests/unit/test_active_consent_route_order.py",
    "docs/security/consent_rejection_audit.md",
    "docs/security/active_consent_route_order.md",
    "scripts/check_consent_rejection_audit.py",
    "scripts/check_active_consent_route_order.py",
    "tests/unit/test_popia_consent_gate_closure_report.py",
    "tests/unit/test_popia_consent_boundary_matrix_check.py",
    "tests/unit/test_generate_popia_consent_boundary_matrix.py",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/security/popia_consent_boundary_check.md",
    "docs/security/popia_consent_boundary_matrix.md",
    "scripts/check_popia_consent_boundary_matrix.py",
    "scripts/generate_popia_consent_boundary_matrix.py",
    "tests/unit/test_ether_onboarding_consent_gate_wiring.py",
    "docs/security/ether_onboarding_consent_gate.md",
    "tests/unit/test_onboarding_consent_gate_wiring.py",
    "tests/unit/test_assessment_consent_gate_wiring.py",
    "docs/security/onboarding_consent_gate.md",
    "docs/security/assessment_consent_gate.md",
    "tests/unit/test_popia_data_rights_consent_boundary.py",
    "tests/unit/test_parent_routes_consent_gate_wiring.py",
    "docs/security/popia_data_rights_consent_boundary.md",
    "docs/security/parent_routes_consent_gate.md",
    "scripts/generate_consent_gate_inventory.py",
    "scripts/check_consent_gate_inventory.py",
    "scripts/check_audit_event_contracts.py",
    ".github/workflows/popia-consent-audit.yml",
    "docs/security/popia_consent_gate_inventory.md",
    "docs/security/popia_consent_gate_allowlist.txt",
    "docs/security/popia_consent_gate_check.md",
    "docs/security/audit_event_contracts.md",
    "docs/security/popia_consent_audit_ci.md",
    "docs/security/POPIA_CONSENT_AUDIT_BASELINE.md",
    "tests/unit/test_generate_consent_gate_inventory.py",
    "tests/unit/test_consent_gate_inventory_check.py",
    "tests/unit/test_audit_event_contracts.py",
    "tests/unit/test_popia_consent_audit_baseline_docs.py",
    "tests/unit/test_popia_consent_audit_ci_contract.py",
)

CONTENT_REQUIREMENTS = {
    "docs/security/consent_rejection_audit.md": (
        "consent.access_rejected",
        "ConsentExpiredError",
    ),
    "docs/security/active_consent_route_order.md": (
        "object authorization must run before active POPIA consent",
    ),
    "docs/security/popia_consent_boundary_matrix.md": (
        "POPIA Consent Boundary Matrix",
        "active_consent_required",
        "rights_exercise_not_active_consent_blocked",
    ),
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md": (
        "POPIA Consent Gate Closure Report",
        "make popia-consent-boundary-check",
        "rights_exercise_not_active_consent_blocked",
    ),
    "docs/security/ether_onboarding_consent_gate.md": (
        "Ether Onboarding Consent Boundary",
        "authenticated_catalog_boundary",
    ),
    "docs/security/onboarding_consent_gate.md": (
        "Onboarding Consent Gate",
        "authenticated catalog boundary",
    ),
    "docs/security/assessment_consent_gate.md": (
        "Assessment Consent Gate",
        "authenticated catalog boundary",
    ),
    "app/api_v2_routers/onboarding.py": (
        "require_active_consent_for_current_user",
        "await require_active_consent_for_current_user(db, current_user, body.learner_id)",
    ),
    "app/api_v2_routers/assessments.py": (
        "require_active_consent_for_current_user",
        "await require_active_consent_for_current_user(db, current_user, request.learner_id)",
    ),
    "docs/security/popia_data_rights_consent_boundary.md": (
        "Data-Subject Rights Workflows",
        "not blocked by active consent",
    ),
    "docs/security/parent_routes_consent_gate.md": (
        "Parent Routes Consent Gate",
        "active POPIA consent",
    ),
    "app/api_v2_routers/popia.py": (
        "require_active_consent_for_current_user",
        "await require_active_consent_for_current_user(db, current_user, learner_id)",
    ),
    "app/api_v2_routers/parents.py": (
        "require_active_consent_for_current_user",
        "await require_active_consent_for_current_user(db, current_user, learner.id)",
        "await require_active_consent_for_current_user(db, current_user, learner_id)",
    ),
    "Makefile": (
        "audit-contract-check:",
        "popia-consent-gate-check:",
        "popia-consent-boundary-check:",
        "popia-consent-order-check:",
        "popia-consent-rejection-audit-check:",
    ),
    "scripts/generate_consent_gate_inventory.py": (
        "ConsentGateRow",
        "CONSENT_MARKERS",
        "LEARNER_DATA_KEYWORDS",
    ),
    "scripts/check_consent_gate_inventory.py": (
        "ALLOWLIST_PATH",
        "--write-baseline",
        "missing_rows",
    ),
    "scripts/check_audit_event_contracts.py": (
        "FourthEstateService",
        "consent.access_rejected",
        "consent.granted",
    ),
    ".github/workflows/popia-consent-audit.yml": (
        "POPIA Consent Audit",
        "make audit-contract-check",
        "make popia-consent-gate-check",
        "make popia-consent-order-check",
        "make popia-consent-rejection-audit-check",
    ),
    "docs/security/POPIA_CONSENT_AUDIT_BASELINE.md": (
        "POPIA Consent and Audit Baseline",
        "Next Hardening Targets",
    ),
}


@dataclass(frozen=True)
class CheckResult:
    category: str
    target: str
    ok: bool
    detail: str


def run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(CheckResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                CheckResult(
                    "content",
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    return results


def main() -> int:
    results = run_checks()
    print("POPIA consent/audit evidence check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} [{result.category}] {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
