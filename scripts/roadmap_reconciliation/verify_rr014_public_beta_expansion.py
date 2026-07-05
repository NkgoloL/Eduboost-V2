#!/usr/bin/env python3
"""Verify RR-014 public beta expansion authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.public_beta.audit_rr014_public_beta_expansion import audit

RR_ID = "RR-014"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR013_RECORD = Path("docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_014_public_beta_expansion_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_014_public_beta_expansion.md")
WORKFLOW = Path(".github/workflows/rr014-public-beta-expansion.yml")
AUDIT_SCRIPT = Path("scripts/public_beta/audit_rr014_public_beta_expansion.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr014_public_beta_expansion_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr014_public_beta_expansion.py")
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
    "public_beta_expansion_readiness_recorded",
    "rr013_advanced_mastery_model_research_valid",
    "expansion_planning_boundary_recorded",
    "controlled_beta_outcome_reviewed",
    "public_beta_scope_bounded",
    "public_beta_success_metrics_defined",
    "public_beta_rollback_criteria_defined",
    "public_beta_cohort_plan_recorded",
    "consent_privacy_attestation_recorded",
    "support_incident_plan_recorded",
    "public_beta_launch_boundary_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr015_external_approvals_remaining_visible",
    "rr016_operational_drills_remaining_visible",
    "rr017_release_safety_controls_remaining_visible",
    "rr018_trustworthy_beta_quality_remaining_visible",
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
    checks: dict[str, bool] = {}

    required_paths = {
        "register": REGISTER,
        "rr013_record": RR013_RECORD,
        "record": RECORD,
        "rr_doc": RR_DOC,
        "workflow": WORKFLOW,
        "audit_script": AUDIT_SCRIPT,
        "capture_script": CAPTURE_SCRIPT,
        "verify_script": VERIFY_SCRIPT,
    }
    for name, path in required_paths.items():
        exists = (root / path).exists()
        checks[f"{name}_exists"] = exists
        if not exists:
            errors.append(f"missing required RR-014 file: {path}")

    register = _read(root, REGISTER)
    checks["register_mentions_rr014"] = "RR-014" in register and "Public beta expansion" in register
    if not checks["register_mentions_rr014"]:
        errors.append("outstanding work register must mention RR-014 public beta expansion")

    rr013 = _json(root, RR013_RECORD)
    checks["rr013_record_valid"] = rr013.get("advanced_mastery_model_research_recorded") is True
    if not checks["rr013_record_valid"]:
        errors.append("RR-013 advanced mastery-model research must be recorded before RR-014")

    makefile = _read(root, MAKEFILE)
    for target in ("rr014-public-beta-expansion-audit", "rr014-public-beta-expansion-check"):
        ok = target in makefile
        checks[f"makefile_target:{target}"] = ok
        if not ok:
            errors.append(f"Makefile missing target: {target}")

    workflow = _read(root, WORKFLOW)
    checks["workflow_mentions_rr014"] = "RR-014 Public Beta Expansion" in workflow
    if not checks["workflow_mentions_rr014"]:
        errors.append("RR-014 workflow must identify the RR-014 check")

    audit_result = audit(root, require_final=False)
    checks["authority_audit_valid"] = audit_result.get("authority_valid") is True
    if not checks["authority_audit_valid"]:
        errors.extend(audit_result.get("errors", []))

    record = _json(root, RECORD)
    if record.get("__json_error__"):
        errors.append(f"RR-014 record JSON invalid: {record['__json_error__']}")
        record = {}
    checks["record_rr_id"] = record.get("rr_id") == RR_ID
    if record and record.get("rr_id") != RR_ID:
        errors.append("RR-014 record must carry rr_id=RR-014")

    for key in BOUNDARY_FALSE_KEYS:
        value = record.get(key)
        checks[f"boundary_false:{key}"] = value is False
        if record and value is not False:
            errors.append(f"RR-014 boundary key must remain false: {key}")

    for key in REQUIRED_TRUE_KEYS:
        checks[f"record_true:{key}"] = record.get(key) is True
        if record and record.get("public_beta_expansion_readiness_recorded") is True and record.get(key) is not True:
            errors.append(f"RR-014 recorded evidence missing true flag: {key}")

    if record and record.get("public_beta_expansion_readiness_recorded") is not True:
        warnings.append("record is still pending evidence capture")

    if record.get("public_beta_expansion_readiness_recorded") is True:
        final_audit = audit(root, require_final=True)
        checks["final_audit_valid"] = final_audit.get("valid") is True
        if not final_audit.get("valid"):
            errors.extend(final_audit.get("errors", []))
        embedded = record.get("public_beta_expansion_audit", {})
        checks["record_embeds_valid_audit"] = isinstance(embedded, dict) and embedded.get("valid") is True
        if not checks["record_embeds_valid_audit"]:
            errors.append("RR-014 record must embed a valid public beta expansion audit")

    structural_errors = [e for e in errors if "recorded evidence missing true flag" not in e]
    authority_valid = len(structural_errors) == 0
    valid = authority_valid and record.get("public_beta_expansion_readiness_recorded") is True and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "public_beta_expansion_readiness_recorded": record.get("public_beta_expansion_readiness_recorded") is True,
        "rr013_advanced_mastery_model_research_valid": record.get("rr013_advanced_mastery_model_research_valid") is True,
        "expansion_planning_boundary_recorded": record.get("expansion_planning_boundary_recorded") is True,
        "controlled_beta_outcome_reviewed": record.get("controlled_beta_outcome_reviewed") is True,
        "public_beta_scope_bounded": record.get("public_beta_scope_bounded") is True,
        "public_beta_success_metrics_defined": record.get("public_beta_success_metrics_defined") is True,
        "public_beta_rollback_criteria_defined": record.get("public_beta_rollback_criteria_defined") is True,
        "public_beta_cohort_plan_recorded": record.get("public_beta_cohort_plan_recorded") is True,
        "consent_privacy_attestation_recorded": record.get("consent_privacy_attestation_recorded") is True,
        "support_incident_plan_recorded": record.get("support_incident_plan_recorded") is True,
        "public_beta_launch_boundary_recorded": record.get("public_beta_launch_boundary_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr015_external_approvals_remaining_visible": record.get("rr015_external_approvals_remaining_visible") is True,
        "rr016_operational_drills_remaining_visible": record.get("rr016_operational_drills_remaining_visible") is True,
        "rr017_release_safety_controls_remaining_visible": record.get("rr017_release_safety_controls_remaining_visible") is True,
        "rr018_trustworthy_beta_quality_remaining_visible": record.get("rr018_trustworthy_beta_quality_remaining_visible") is True,
        "public_beta_expansion_authorised": record.get("public_beta_expansion_authorised"),
        "public_beta_live_traffic_authorised": record.get("public_beta_live_traffic_authorised"),
        "expanded_learner_data_migration_authorised": record.get("expanded_learner_data_migration_authorised"),
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "release_tag_authorised": record.get("release_tag_authorised"),
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    ok = result["authority_valid"] if args.authority_only else result["valid"]
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(ok))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
