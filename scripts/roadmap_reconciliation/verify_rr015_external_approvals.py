#!/usr/bin/env python3
"""Verify RR-015 external approvals authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.approvals.audit_rr015_external_approvals import audit

RR_ID = "RR-015"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR014_RECORD = Path("docs/roadmap/reconciliation/rr_014_public_beta_expansion_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_015_external_approvals_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_015_external_approvals.md")
WORKFLOW = Path(".github/workflows/rr015-external-approvals.yml")
AUDIT_SCRIPT = Path("scripts/approvals/audit_rr015_external_approvals.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr015_external_approvals_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr015_external_approvals.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "public_beta_expansion_authorised",
    "public_beta_live_traffic_authorised",
    "expanded_learner_data_migration_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "runtime_kg_implementation_claimed",
)

REQUIRED_TRUE_KEYS = (
    "external_approvals_recorded",
    "rr014_public_beta_expansion_valid",
    "security_review_approved",
    "popia_privacy_review_approved",
    "legal_review_approved",
    "caps_content_review_approved",
    "release_owner_go_no_go_signoff_recorded",
    "external_approval_boundary_recorded",
    "repository_only_approval_substitution_blocked",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr016_operational_drills_remaining_visible",
    "rr017_release_safety_controls_remaining_visible",
    "rr018_trustworthy_beta_quality_remaining_visible",
)


_ARCHIVE = Path("archive/github_workflows")


def _resolve_wf(root: Path, path: Path) -> Path:
    """Return root/path, with archive fallback for missing workflow files."""
    full = root / path
    if not full.exists() and str(path).startswith(".github/workflows/"):
        archived = root / _ARCHIVE / path.name
        if archived.exists():
            return archived
    return full


def _read(root: Path, path: Path) -> str:
    full = _resolve_wf(root, path)
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
    checks: dict[str, bool] = {}

    required_paths = {
        "register": REGISTER,
        "rr014_record": RR014_RECORD,
        "record": RECORD,
        "rr_doc": RR_DOC,
        "workflow": WORKFLOW,
        "audit_script": AUDIT_SCRIPT,
        "capture_script": CAPTURE_SCRIPT,
        "verify_script": VERIFY_SCRIPT,
    }
    for name, path in required_paths.items():
        exists = _resolve_wf(root, path).exists()
        checks[f"{name}_exists"] = exists
        if not exists:
            errors.append(f"missing required RR-015 file: {path}")

    register = _read(root, REGISTER)
    checks["register_mentions_rr015"] = "RR-015" in register and "External approval" in register
    if not checks["register_mentions_rr015"]:
        errors.append("outstanding work register must mention RR-015 external approval")

    rr014 = _json(root, RR014_RECORD)
    checks["rr014_record_valid"] = rr014.get("public_beta_expansion_readiness_recorded") is True
    if not checks["rr014_record_valid"]:
        errors.append("RR-014 public beta expansion readiness must be recorded before RR-015")

    makefile = _read(root, MAKEFILE)
    for target in ("rr015-external-approvals-audit", "rr015-external-approvals-check"):
        ok = target in makefile
        checks[f"makefile_target:{target}"] = ok
        if not ok:
            errors.append(f"Makefile missing target: {target}")

    workflow = _read(root, WORKFLOW)
    checks["workflow_mentions_rr015"] = "RR-015 External Approvals" in workflow
    if not checks["workflow_mentions_rr015"]:
        errors.append("RR-015 workflow must identify the RR-015 check")

    audit_result = audit(root, require_final=False)
    checks["authority_audit_valid"] = audit_result.get("authority_valid") is True
    if not checks["authority_audit_valid"]:
        errors.extend(audit_result.get("errors", []))

    record = _json(root, RECORD)
    if record.get("__json_error__"):
        errors.append(f"RR-015 record JSON invalid: {record['__json_error__']}")
        record = {}
    checks["record_rr_id"] = record.get("rr_id") == RR_ID
    if record and record.get("rr_id") != RR_ID:
        errors.append("RR-015 record must carry rr_id=RR-015")

    for key in BOUNDARY_FALSE_KEYS:
        value = record.get(key)
        checks[f"boundary_false:{key}"] = value is False
        if record and value is not False:
            errors.append(f"RR-015 boundary key must remain false: {key}")

    for key in REQUIRED_TRUE_KEYS:
        checks[f"record_true:{key}"] = record.get(key) is True
        if record and record.get("external_approvals_recorded") is True and record.get(key) is not True:
            errors.append(f"RR-015 recorded evidence missing true flag: {key}")

    if record and record.get("external_approvals_recorded") is not True:
        warnings.append("record is still pending evidence capture")

    if record.get("external_approvals_recorded") is True:
        final_audit = audit(root, require_final=True)
        checks["final_audit_valid"] = final_audit.get("valid") is True
        if not final_audit.get("valid"):
            errors.extend(final_audit.get("errors", []))
        embedded = record.get("external_approvals_audit", {})
        checks["record_embeds_valid_audit"] = isinstance(embedded, dict) and embedded.get("valid") is True
        if not checks["record_embeds_valid_audit"]:
            errors.append("RR-015 record must embed a valid external approvals audit")

    structural_errors = [e for e in errors if "recorded evidence missing true flag" not in e]
    authority_valid = len(structural_errors) == 0
    valid = authority_valid and record.get("external_approvals_recorded") is True and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "external_approvals_recorded": record.get("external_approvals_recorded") is True,
        "rr014_public_beta_expansion_valid": record.get("rr014_public_beta_expansion_valid") is True,
        "security_review_approved": record.get("security_review_approved") is True,
        "popia_privacy_review_approved": record.get("popia_privacy_review_approved") is True,
        "legal_review_approved": record.get("legal_review_approved") is True,
        "caps_content_review_approved": record.get("caps_content_review_approved") is True,
        "release_owner_go_no_go_signoff_recorded": record.get("release_owner_go_no_go_signoff_recorded") is True,
        "external_approval_boundary_recorded": record.get("external_approval_boundary_recorded") is True,
        "repository_only_approval_substitution_blocked": record.get("repository_only_approval_substitution_blocked") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr016_operational_drills_remaining_visible": record.get("rr016_operational_drills_remaining_visible") is True,
        "rr017_release_safety_controls_remaining_visible": record.get("rr017_release_safety_controls_remaining_visible") is True,
        "rr018_trustworthy_beta_quality_remaining_visible": record.get("rr018_trustworthy_beta_quality_remaining_visible") is True,
        "public_beta_expansion_authorised": record.get("public_beta_expansion_authorised") is True,
        "public_beta_live_traffic_authorised": record.get("public_beta_live_traffic_authorised") is True,
        "expanded_learner_data_migration_authorised": record.get("expanded_learner_data_migration_authorised") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed") is True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    out = result if not args.authority_only else {**result, "valid": result["authority_valid"]}
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print("valid=" + str(out["valid"]))
    return 0 if out["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
