#!/usr/bin/env python3
"""Verify RR-018 trustworthy beta product quality authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.product_quality.audit_rr018_trustworthy_beta_quality import audit

RR_ID = "RR-018"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RECORD = Path("docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality_record.json")
RR017_RECORD = Path("docs/roadmap/reconciliation/rr_017_release_safety_controls_record.json")
BOUNDARY_FALSE_KEYS = [
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "runtime_kg_implementation_claimed",
]
REQUIRED_TRUE_KEYS = [
    "trustworthy_beta_product_quality_recorded",
    "rr017_release_safety_controls_valid",
    "feedback_report_issue_button_validated",
    "content_correction_workflow_recorded",
    "human_review_queue_recorded",
    "educator_caps_priority_review_recorded",
    "content_correction_sla_recorded",
    "guardian_feedback_privacy_boundary_recorded",
    "no_learner_pii_in_feedback_evidence",
    "trustworthy_beta_quality_boundary_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr016_clean_git_state_caveat_visible",
    "rr017_release_safety_controls_boundary_visible",
    "all_reconciled_rr_items_addressed_through_rr018",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)

    def p(path: Path) -> Path:
        return root / path

    audit_result = audit(root)
    record = _json(p(RECORD))
    rr017 = _json(p(RR017_RECORD))
    register = _read(p(REGISTER))
    errors: list[str] = []
    warnings: list[str] = []

    rr017_valid = rr017.get("release_safety_controls_recorded") is True and rr017.get("rr_id") == "RR-017"
    register_has_rr018 = RR_ID in register and "Trustworthy beta" in register
    if not register_has_rr018:
        errors.append("RR-018 must remain listed in outstanding_work_register.md")
    if record.get("rr_id") != RR_ID:
        errors.append(f"record rr_id must be {RR_ID}")
    if not rr017_valid:
        errors.append("RR-017 release safety controls must be valid before RR-018 capture")
    if not audit_result["authority_valid"]:
        errors.extend([f"authority audit failed: {e}" for e in audit_result.get("errors", [])])

    if record.get("trustworthy_beta_product_quality_recorded") is True:
        if not audit_result["final_valid"]:
            errors.extend([f"final trustworthy-beta quality evidence failed: {e}" for e in audit_result.get("errors", [])])
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
    else:
        warnings.append("record is still pending RR-018 evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    authority_errors = [
        e for e in errors
        if not e.startswith("record flag must be true") and not e.startswith("final trustworthy-beta quality evidence failed")
    ]
    authority_valid = not authority_errors and audit_result["authority_valid"] and rr017_valid and register_has_rr018
    valid = authority_valid and record.get("trustworthy_beta_product_quality_recorded") is True and not errors
    if record.get("trustworthy_beta_product_quality_recorded") is not True:
        valid = False

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "audit": audit_result,
        "errors": errors,
        "warnings": warnings,
        "rr017_release_safety_controls_valid": rr017_valid,
        "trustworthy_beta_product_quality_recorded": record.get("trustworthy_beta_product_quality_recorded") is True,
        "feedback_report_issue_button_validated": record.get("feedback_report_issue_button_validated") is True,
        "content_correction_workflow_recorded": record.get("content_correction_workflow_recorded") is True,
        "human_review_queue_recorded": record.get("human_review_queue_recorded") is True,
        "educator_caps_priority_review_recorded": record.get("educator_caps_priority_review_recorded") is True,
        "content_correction_sla_recorded": record.get("content_correction_sla_recorded") is True,
        "guardian_feedback_privacy_boundary_recorded": record.get("guardian_feedback_privacy_boundary_recorded") is True,
        "no_learner_pii_in_feedback_evidence": record.get("no_learner_pii_in_feedback_evidence") is True,
        "trustworthy_beta_quality_boundary_recorded": record.get("trustworthy_beta_quality_boundary_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr016_clean_git_state_caveat_visible": record.get("rr016_clean_git_state_caveat_visible") is True,
        "rr017_release_safety_controls_boundary_visible": record.get("rr017_release_safety_controls_boundary_visible") is True,
        "all_reconciled_rr_items_addressed_through_rr018": record.get("all_reconciled_rr_items_addressed_through_rr018") is True,
        **{key: record.get(key) for key in BOUNDARY_FALSE_KEYS},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"RR-018 trustworthy beta product quality valid: {result['valid']}")
        print(f"RR-018 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
