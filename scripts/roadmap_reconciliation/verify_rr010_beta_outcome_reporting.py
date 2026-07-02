#!/usr/bin/env python3
"""Verify RR-010 beta outcome reporting authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.beta_outcomes.audit_rr010_beta_outcome_reporting import audit

RR_ID = "RR-010"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR009_RECORD = Path("docs/roadmap/reconciliation/rr_009_governance_process_reconciliation_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_010_beta_outcome_reporting_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_010_beta_outcome_reporting.md")
WORKFLOW = Path(".github/workflows/rr010-beta-outcome-reporting.yml")
AUDIT_SCRIPT = Path("scripts/beta_outcomes/audit_rr010_beta_outcome_reporting.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr010_beta_outcome_reporting_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr010_beta_outcome_reporting.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)

REQUIRED_TRUE_KEYS = (
    "beta_outcome_reporting_recorded",
    "minimum_beta_duration_met",
    "cohort_size_requirement_met",
    "educator_feedback_collected",
    "uptime_target_met",
    "p95_diagnostic_latency_target_met",
    "zero_critical_security_incidents",
    "zero_pii_exposure_events",
    "zero_consent_incidents",
    "educator_content_approval_threshold_met",
    "learner_session_completion_threshold_met",
    "backup_restore_drill_references_recorded",
    "weekly_health_reviews_completed",
    "beta_outcome_report_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
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
    rr009_record = _json(root, RR009_RECORD)
    record = _json(root, RECORD)
    rr_doc = _read(root, RR_DOC)
    workflow = _read(root, WORKFLOW)
    makefile = _read(root, MAKEFILE)
    audit_result = audit(root, require_final=record.get("beta_outcome_reporting_recorded") is True)

    checks = {
        "rr010_in_outstanding_register": RR_ID in register and "Beta period with real learner feedback" in register,
        "rr009_predecessor_recorded": rr009_record.get("governance_process_reconciliation_recorded") is True,
        "rr_doc_exists": (root / RR_DOC).exists(),
        "record_exists": (root / RECORD).exists(),
        "workflow_exists": (root / WORKFLOW).exists(),
        "audit_script_exists": (root / AUDIT_SCRIPT).exists(),
        "capture_script_exists": (root / CAPTURE_SCRIPT).exists(),
        "verify_script_exists": (root / VERIFY_SCRIPT).exists(),
        "rr_doc_cites_register_id": RR_ID in rr_doc,
        "rr_doc_preserves_boundaries": "public beta" in rr_doc.lower() and "not authorised" in rr_doc and "Runtime KG" in rr_doc,
        "workflow_runs_verifier": "verify_rr010_beta_outcome_reporting.py" in workflow,
        "makefile_has_rr010_audit_target": "rr010-beta-outcome-audit" in makefile,
        "makefile_has_rr010_check_target": "rr010-beta-outcome-check" in makefile,
        "authority_audit_valid": audit_result.get("authority_valid") is True,
    }

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if audit_result.get("errors"):
        for error in audit_result["errors"]:
            if record.get("beta_outcome_reporting_recorded") is True or not (
                error.startswith("missing final")
                or "final marker" in error
                or "metrics" in error.lower()
                or "numeric threshold" in error
            ):
                errors.append(f"audit error: {error}")
    if audit_result.get("warnings"):
        warnings.extend(audit_result["warnings"])

    if record.get("__json_error__"):
        errors.append(f"record JSON invalid: {record['__json_error__']}")
    elif record:
        if record.get("rr_id") != RR_ID:
            errors.append(f"record rr_id must be {RR_ID}")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"boundary flag must remain false: {key}")
        if record.get("beta_outcome_reporting_recorded") is True:
            for key in REQUIRED_TRUE_KEYS:
                if record.get(key) is not True:
                    errors.append(f"record flag must be true after evidence capture: {key}")
            if not isinstance(record.get("beta_outcome_audit"), dict):
                errors.append("beta_outcome_audit must be embedded after capture")
            if not record.get("beta_outcome_audit", {}).get("final_outputs_valid"):
                errors.append("beta_outcome_audit.final_outputs_valid must be true after capture")
        else:
            warnings.append("record is still pending evidence capture")
    else:
        errors.append("record JSON is missing")

    authority_errors = [
        err for err in errors
        if not err.startswith("record flag must be true")
        and err != "beta_outcome_audit must be embedded after capture"
        and err != "beta_outcome_audit.final_outputs_valid must be true after capture"
    ]
    authority_valid = not authority_errors
    valid = not errors and record.get("beta_outcome_reporting_recorded") is True

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "beta_outcome_reporting_recorded": record.get("beta_outcome_reporting_recorded") is True,
        "minimum_beta_duration_met": record.get("minimum_beta_duration_met") is True,
        "cohort_size_requirement_met": record.get("cohort_size_requirement_met") is True,
        "educator_feedback_collected": record.get("educator_feedback_collected") is True,
        "uptime_target_met": record.get("uptime_target_met") is True,
        "p95_diagnostic_latency_target_met": record.get("p95_diagnostic_latency_target_met") is True,
        "zero_critical_security_incidents": record.get("zero_critical_security_incidents") is True,
        "zero_pii_exposure_events": record.get("zero_pii_exposure_events") is True,
        "zero_consent_incidents": record.get("zero_consent_incidents") is True,
        "educator_content_approval_threshold_met": record.get("educator_content_approval_threshold_met") is True,
        "learner_session_completion_threshold_met": record.get("learner_session_completion_threshold_met") is True,
        "backup_restore_drill_references_recorded": record.get("backup_restore_drill_references_recorded") is True,
        "weekly_health_reviews_completed": record.get("weekly_health_reviews_completed") is True,
        "beta_outcome_report_recorded": record.get("beta_outcome_report_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
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
