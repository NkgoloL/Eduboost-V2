#!/usr/bin/env python3
"""Verify TA Phase 09 hosted-CI / merge-readiness authority assets.

This verifier is intentionally static. It proves the local authority harness is
present and wired. It does not claim hosted GitHub Actions success; that claim is
made only by verify_hosted_ci_merge_readiness_evidence.py against a supplied CI
status artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
PHASE_DOC = ROOT / "docs/roadmap/execution/technical_audit_remediation/09_hosted_ci_merge_readiness_authority.md"
REQUIRED_FILES = [
    Path("scripts/audit_remediation/verify_hosted_ci_merge_readiness_authority.py"),
    Path("scripts/audit_remediation/collect_hosted_ci_merge_readiness_evidence.sh"),
    Path("scripts/audit_remediation/verify_hosted_ci_merge_readiness_evidence.py"),
    Path("tests/unit/audit_remediation/test_hosted_ci_merge_readiness_authority.py"),
    Path("docs/roadmap/execution/technical_audit_remediation/09_hosted_ci_merge_readiness_authority.md"),
]
PRIOR_EVIDENCE_PATHS = {
    "backend_fast": Path("docs/release-evidence/technical-audit/backend-fast-gate/evidence_index.md"),
    "frontend_tooling": Path("docs/release-evidence/technical-audit/frontend-tooling-authority/evidence_index.md"),
    "ci_authority_workflow": Path("docs/release-evidence/technical-audit/ci-authority-workflow/evidence_index.md"),
    "dependency_scan_enforcement": Path("docs/release-evidence/technical-audit/dependency-scan-enforcement/evidence_index.md"),
    "e2e_playwright_authority": Path("docs/release-evidence/technical-audit/e2e-playwright-authority/evidence_index.md"),
    "openapi_frontend_contract": Path("docs/release-evidence/technical-audit/openapi-frontend-contract/evidence_index.md"),
    "remote_ci_branch_integration": Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/evidence_index.md"),
}
PRIOR_BLOCKERS = [
    "TA-BACKEND-FAST-001",
    "TA-FRONTEND-001",
    "TA-CI-001",
    "TA-SECURITY-001",
    "TA-E2E-001",
    "TA-OPENAPI-001",
    "TA-REMOTE-CI-001",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_blocker(register: dict[str, Any], blocker_id: str) -> dict[str, Any] | None:
    blockers = register.get("remaining_release_blockers_after_reset")
    if not isinstance(blockers, list):
        return None
    for item in blockers:
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    return None


def verify() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        checked.append(str(rel))
        if not path.exists():
            errors.append(f"required Phase 09 file missing: {rel}")

    if not REGISTER.exists():
        errors.append(f"blocker register missing: {REGISTER.relative_to(ROOT)}")
        register: dict[str, Any] = {}
    else:
        try:
            register = _load_json(REGISTER)
            checked.append(str(REGISTER.relative_to(ROOT)))
        except Exception as exc:  # pragma: no cover
            register = {}
            errors.append(f"blocker register is not valid JSON: {exc}")

    if register:
        phase09 = _find_blocker(register, "TA-HOSTED-CI-001")
        if phase09 is None:
            errors.append("TA-HOSTED-CI-001 blocker entry missing")
        else:
            checked.append("TA-HOSTED-CI-001")
            if phase09.get("status") not in {"hosted_ci_merge_readiness_authority_ready", "evidence_recorded"}:
                errors.append("TA-HOSTED-CI-001 status is not Phase 09-ready/evidence_recorded")
            if phase09.get("remote_ci_run_claimed") is not False and phase09.get("remote_ci_run_claimed") is not True:
                errors.append("TA-HOSTED-CI-001 remote_ci_run_claimed must be a boolean")
            if phase09.get("release_readiness_claimed") is not False:
                errors.append("TA-HOSTED-CI-001 must not claim release readiness")
        for blocker_id in PRIOR_BLOCKERS:
            prior = _find_blocker(register, blocker_id)
            if prior is None:
                warnings.append(f"prior blocker not found in register: {blocker_id}")
                continue
            checked.append(blocker_id)
            if prior.get("status") != "evidence_recorded":
                warnings.append(f"prior blocker {blocker_id} is not evidence_recorded")

    for name, rel in PRIOR_EVIDENCE_PATHS.items():
        checked.append(str(rel))
        if not (ROOT / rel).exists():
            warnings.append(f"prior evidence index not present yet for {name}: {rel}")

    if PHASE_DOC.exists():
        text = PHASE_DOC.read_text(encoding="utf-8")
        for phrase in [
            "Hosted CI Run Evidence",
            "remote CI success is not inferred",
            "release readiness is not claimed",
        ]:
            if phrase not in text:
                errors.append(f"Phase 09 doc missing required phrase: {phrase}")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
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
