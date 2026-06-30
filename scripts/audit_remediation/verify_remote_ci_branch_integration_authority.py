#!/usr/bin/env python3
"""Verify TA Phase 08 Remote CI / Branch Integration authority assets.

This verifier is intentionally static. It proves that the branch-integration
control plane exists and that prior local/static gates have evidence bundles
available. It does not claim hosted GitHub Actions success.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = ROOT / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
PHASE_DOC = ROOT / "docs/roadmap/execution/technical_audit_remediation/08_remote_ci_branch_integration_authority.md"

REQUIRED_PRIOR_EVIDENCE = {
    "backend_fast_gate": {
        "dir": "docs/release-evidence/technical-audit/backend-fast-gate",
        "verifier": "scripts/audit_remediation/verify_backend_fast_evidence.py",
    },
    "frontend_tooling_authority": {
        "dir": "docs/release-evidence/technical-audit/frontend-tooling-authority",
        "verifier": "scripts/audit_remediation/verify_frontend_tooling_evidence.py",
    },
    "ci_authority_workflow": {
        "dir": "docs/release-evidence/technical-audit/ci-authority-workflow",
        "verifier": "scripts/audit_remediation/verify_ci_authority_workflow_evidence.py",
    },
    "dependency_scan_enforcement": {
        "dir": "docs/release-evidence/technical-audit/dependency-scan-enforcement",
        "verifier": "scripts/audit_remediation/verify_dependency_scan_evidence.py",
    },
    "e2e_playwright_authority": {
        "dir": "docs/release-evidence/technical-audit/e2e-playwright-authority",
        "verifier": "scripts/audit_remediation/verify_e2e_playwright_evidence.py",
    },
    "openapi_frontend_contract": {
        "dir": "docs/release-evidence/technical-audit/openapi-frontend-contract",
        "verifier": "scripts/audit_remediation/verify_openapi_frontend_contract_evidence.py",
    },
}

REQUIRED_ASSETS = [
    PHASE_DOC,
    ROOT / "scripts/audit_remediation/verify_remote_ci_branch_integration_authority.py",
    ROOT / "scripts/audit_remediation/collect_remote_ci_branch_integration_evidence.sh",
    ROOT / "scripts/audit_remediation/verify_remote_ci_branch_integration_evidence.py",
    ROOT / "tests/unit/audit_remediation/test_remote_ci_branch_integration_authority.py",
]


def _run_git(args: list[str]) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"missing required JSON file: {path.relative_to(ROOT)}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"expected object JSON in {path.relative_to(ROOT)}")
        return {}
    return data


def _find_blocker(register: dict[str, Any], blocker_id: str) -> dict[str, Any] | None:
    blockers = register.get("remaining_release_blockers_after_reset")
    if isinstance(blockers, list):
        for item in blockers:
            if isinstance(item, dict) and item.get("id") == blocker_id:
                return item
    return None


def verify() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_ASSETS:
        if not path.exists():
            errors.append(f"missing authority asset: {path.relative_to(ROOT)}")

    register = _load_json(REGISTER_PATH, errors)
    if register:
        terminal_closed = (
            register.get("status") in {
                "phase_12_technical_audit_remediation_closed",
                "phase_13b_post_merge_baseline_recorded",
            }
            or register.get("active_slice") in {
                "technical-audit-remediation-closed",
                "technical-audit-post-merge-baseline-recorded",
            }
        )
        if not terminal_closed and register.get("active_slice") != "08-remote-ci-branch-integration-authority":
            errors.append(
                "blocker_register.active_slice must be 08-remote-ci-branch-integration-authority"
            )
        status = register.get("status")
        if not terminal_closed and status not in {
            "phase_08_remote_ci_branch_integration_authority_ready",
            "phase_08_remote_ci_branch_integration_authority_closed",
        }:
            errors.append(
                "blocker_register.status must identify Phase 08 remote CI branch integration authority"
            )
        blocker = _find_blocker(register, "TA-REMOTE-CI-001")
        if not blocker:
            errors.append("missing TA-REMOTE-CI-001 in blocker register")
        else:
            if blocker.get("remote_ci_run_claimed") not in {False, True}:
                errors.append("TA-REMOTE-CI-001.remote_ci_run_claimed must be boolean")
            if blocker.get("full_release_readiness_claimed") is not False:
                errors.append("TA-REMOTE-CI-001.full_release_readiness_claimed must remain false")
            if blocker.get("branch_integration_authority_result") not in {"pending", "valid"}:
                errors.append("TA-REMOTE-CI-001.branch_integration_authority_result must be pending or valid")

    prior_evidence: dict[str, Any] = {}
    for name, spec in REQUIRED_PRIOR_EVIDENCE.items():
        evidence_dir = ROOT / spec["dir"]
        verifier = ROOT / spec["verifier"]
        prior_evidence[name] = {
            "evidence_dir": spec["dir"],
            "verifier": spec["verifier"],
            "evidence_dir_present": evidence_dir.is_dir(),
            "verifier_present": verifier.is_file(),
            "evidence_index_present": (evidence_dir / "evidence_index.md").is_file(),
        }
        if not evidence_dir.is_dir():
            errors.append(f"missing prior evidence directory: {spec['dir']}")
        if not verifier.is_file():
            errors.append(f"missing prior evidence verifier: {spec['verifier']}")
        if not (evidence_dir / "evidence_index.md").is_file():
            errors.append(f"missing prior evidence index: {spec['dir']}/evidence_index.md")

    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _run_git(["rev-parse", "--short=10", "HEAD"])
    status_short = _run_git(["status", "--short"])
    if status_short:
        warnings.append("working tree has uncommitted changes; collect final evidence from a clean tree")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "phase": "08-remote-ci-branch-integration-authority",
        "remote_ci_run_claimed": False,
        "full_release_readiness_claimed": False,
        "prior_evidence": prior_evidence,
        "git": {
            "branch": branch,
            "head": head,
            "working_tree_clean": status_short == "" if status_short is not None else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
