#!/usr/bin/env python3
"""Verify RR-009 governance/process reconciliation authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-009"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR008_RECORD = Path("docs/roadmap/reconciliation/rr_008_operational_readiness_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_009_governance_process_reconciliation_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_009_governance_process_reconciliation.md")
CURRENT_STATE = Path("docs/current_state.md")
ADR_README = Path("docs/adr/README.md")
MANIFEST = Path("docs/governance/rr009_governance_process_manifest.json")
POLICY = Path("docs/governance/rr009_governance_process_policy.md")
CURRENT_STATE_CADENCE = Path("docs/governance/rr009_current_state_refresh_cadence.md")
ADR_INDEX_DOC = Path("docs/governance/rr009_adr_index_completion.md")
EXTERNAL_TODO = Path("docs/governance/rr009_external_todo_ownership_register.md")
BRANCH_DOC = Path("docs/governance/rr009_branch_protection_release_docs.md")
RELEASE_BRANCH_DOC = Path("docs/release/current/branch_protection_evidence.md")
RELEASE_README = Path("docs/release/current/README.md")
WORKFLOW = Path(".github/workflows/rr009-governance-process.yml")
AUDIT_SCRIPT = Path("scripts/governance/audit_rr009_governance_process.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr009_governance_process_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr009_governance_process.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_KEYS = (
    "governance_process_reconciliation_recorded",
    "current_state_refresh_cadence_recorded",
    "adr_index_completed",
    "external_todo_ownership_recorded",
    "branch_protection_release_docs_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr010_beta_outcome_reporting_remaining_visible",
    "rr015_external_approvals_remaining_visible",
    "rr016_operational_drills_remaining_visible",
)


def _read(root: Path, path: Path) -> str:
    full = root / path
    return full.read_text(encoding="utf-8") if full.exists() else ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    register = _read(root, REGISTER)
    rr008_record = _json(root, RR008_RECORD)
    record = _json(root, RECORD)
    manifest = _json(root, MANIFEST)
    rr_doc = _read(root, RR_DOC)
    current_state = _read(root, CURRENT_STATE)
    adr_readme = _read(root, ADR_README)
    policy = _read(root, POLICY)
    current_state_cadence = _read(root, CURRENT_STATE_CADENCE)
    adr_index_doc = _read(root, ADR_INDEX_DOC)
    external_todo = _read(root, EXTERNAL_TODO)
    branch_doc = _read(root, BRANCH_DOC)
    release_branch_doc = _read(root, RELEASE_BRANCH_DOC)
    release_readme = _read(root, RELEASE_README)
    workflow = _read(root, WORKFLOW)
    audit_script = _read(root, AUDIT_SCRIPT)
    makefile = _read(root, MAKEFILE)

    checks = {
        "rr009_in_outstanding_register": RR_ID in register and "Governance and process" in register,
        "rr008_predecessor_recorded": rr008_record.get("operational_readiness_recorded") is True,
        "rr_doc_exists": (root / RR_DOC).exists(),
        "record_exists": (root / RECORD).exists(),
        "current_state_exists": (root / CURRENT_STATE).exists(),
        "adr_readme_exists": (root / ADR_README).exists(),
        "manifest_exists": (root / MANIFEST).exists(),
        "policy_exists": (root / POLICY).exists(),
        "current_state_cadence_exists": (root / CURRENT_STATE_CADENCE).exists(),
        "adr_index_doc_exists": (root / ADR_INDEX_DOC).exists(),
        "external_todo_exists": (root / EXTERNAL_TODO).exists(),
        "branch_doc_exists": (root / BRANCH_DOC).exists(),
        "release_branch_doc_exists": (root / RELEASE_BRANCH_DOC).exists(),
        "release_readme_exists": (root / RELEASE_README).exists(),
        "workflow_exists": (root / WORKFLOW).exists(),
        "audit_script_exists": (root / AUDIT_SCRIPT).exists(),
        "capture_script_exists": (root / CAPTURE_SCRIPT).exists(),
        "verify_script_exists": (root / VERIFY_SCRIPT).exists(),
        "rr_doc_cites_register_id": RR_ID in rr_doc,
        "current_state_reviewed_2026_07_02": "last_reviewed:" in current_state,
        "current_state_refresh_marker_present": "Current-state refresh cadence recorded: true" in current_state,
        "current_state_mentions_rr_rule": "RR-###" in current_state and "outstanding_work_register.md" in current_state,
        "adr_index_marker_present": "ADR index completion recorded: true" in adr_readme and "Frontend ADR index" in adr_readme,
        "external_todo_marker_present": "External TODO ownership recorded: true" in external_todo,
        "external_todo_has_owners_dates": "Owner" in external_todo and "Target review date" in external_todo,
        "release_docs_branch_marker_present": "Branch protection reflected in canonical release docs: true" in release_branch_doc,
        "release_readme_links_branch_doc": "branch_protection_evidence.md" in release_readme,
        "policy_preserves_rr003_caveat": "RR-003" in policy and "0.0" in policy,
        "policy_preserves_rr006_caveat": "RR-006" in policy and "non-required" in policy,
        "policy_preserves_boundaries": "Runtime KG" in policy and "not authorised" in policy,
        "policy_marks_future_rr_remaining": "RR-010" in policy and "RR-015" in policy and "RR-016" in policy,
        "current_state_cadence_marker_present": "Current-state refresh cadence recorded: true" in current_state_cadence,
        "adr_index_doc_marker_present": "ADR index completion recorded: true" in adr_index_doc,
        "branch_doc_marker_present": "Branch protection release docs recorded: true" in branch_doc,
        "workflow_runs_verifier": "verify_rr009_governance_process.py" in workflow,
        "audit_script_checks_all_gate_areas": all(token in audit_script for token in (
            "current_state_refresh_cadence_recorded",
            "adr_index_completed",
            "external_todo_ownership_recorded",
            "branch_protection_release_docs_recorded",
        )),
        "makefile_has_rr009_audit_target": "rr009-governance-process-audit" in makefile,
        "makefile_has_rr009_check_target": "rr009-governance-process-check" in makefile,
    }

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if manifest.get("__json_error__"):
        errors.append(f"manifest JSON invalid: {manifest['__json_error__']}")
    elif manifest:
        for key in REQUIRED_TRUE_KEYS[1:]:
            if manifest.get(key) is not True:
                errors.append(f"manifest flag must be true: {key}")
        for key in BOUNDARY_FALSE_KEYS:
            if manifest.get(key) is not False:
                errors.append(f"manifest boundary flag must be false: {key}")
    else:
        errors.append("RR-009 manifest is missing")

    if record.get("__json_error__"):
        errors.append(f"record JSON invalid: {record['__json_error__']}")
    elif record:
        if record.get("rr_id") != RR_ID:
            errors.append(f"record rr_id must be {RR_ID}")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"boundary flag must remain false: {key}")
        if record.get("governance_process_reconciliation_recorded") is True:
            for key in REQUIRED_TRUE_KEYS:
                if record.get(key) is not True:
                    errors.append(f"record flag must be true after evidence capture: {key}")
            if not isinstance(record.get("governance_process_audit"), dict):
                errors.append("governance_process_audit must be embedded after capture")
        else:
            warnings.append("record is still pending evidence capture")
    else:
        errors.append("record JSON is missing")

    authority_errors = [
        err for err in errors
        if not err.startswith("record flag must be true")
        and err != "governance_process_audit must be embedded after capture"
    ]
    authority_valid = not authority_errors
    valid = not errors and record.get("governance_process_reconciliation_recorded") is True

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "governance_process_reconciliation_recorded": record.get("governance_process_reconciliation_recorded") is True,
        "current_state_refresh_cadence_recorded": record.get("current_state_refresh_cadence_recorded") is True,
        "adr_index_completed": record.get("adr_index_completed") is True,
        "external_todo_ownership_recorded": record.get("external_todo_ownership_recorded") is True,
        "branch_protection_release_docs_recorded": record.get("branch_protection_release_docs_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr010_beta_outcome_reporting_remaining_visible": record.get("rr010_beta_outcome_reporting_remaining_visible") is True,
        "rr015_external_approvals_remaining_visible": record.get("rr015_external_approvals_remaining_visible") is True,
        "rr016_operational_drills_remaining_visible": record.get("rr016_operational_drills_remaining_visible") is True,
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "release_tag_authorised": record.get("release_tag_authorised"),
        "public_beta_authorised": record.get("public_beta_authorised"),
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.authority_only:
        result = dict(result)
        result["valid"] = result["authority_valid"]
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
