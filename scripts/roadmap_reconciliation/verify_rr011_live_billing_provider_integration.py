#!/usr/bin/env python3
"""Verify RR-011 live billing provider integration authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.billing.audit_rr011_live_billing_provider_integration import audit

RR_ID = "RR-011"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR010_RECORD = Path("docs/roadmap/reconciliation/rr_010_beta_outcome_reporting_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_011_live_billing_provider_integration_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_011_live_billing_provider_integration.md")
WORKFLOW = Path(".github/workflows/rr011-live-billing-provider-integration.yml")
AUDIT_SCRIPT = Path("scripts/billing/audit_rr011_live_billing_provider_integration.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr011_live_billing_provider_integration_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr011_live_billing_provider_integration.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)

REQUIRED_TRUE_KEYS = (
    "live_billing_provider_integration_recorded",
    "rr010_beta_outcome_reporting_valid",
    "billing_provider_decision_recorded",
    "hosted_checkout_provider_attested",
    "hosted_checkout_sandbox_validated",
    "webhook_endpoint_validation_recorded",
    "webhook_signature_validation_recorded",
    "webhook_idempotency_validation_recorded",
    "pricing_catalogue_approved",
    "no_raw_card_storage_confirmed",
    "secrets_not_committed_confirmed",
    "billing_launch_boundary_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr012_production_telemetry_remaining_visible",
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
    rr010_record = _json(root, RR010_RECORD)
    record = _json(root, RECORD)
    rr_doc = _read(root, RR_DOC)
    workflow = _read(root, WORKFLOW)
    makefile = _read(root, MAKEFILE)
    audit_result = audit(root, require_final=record.get("live_billing_provider_integration_recorded") is True)

    checks = {
        "rr011_in_outstanding_register": RR_ID in register and "Live billing provider integration" in register,
        "rr010_predecessor_recorded": rr010_record.get("beta_outcome_reporting_recorded") is True,
        "rr_doc_exists": (root / RR_DOC).exists(),
        "record_exists": (root / RECORD).exists(),
        "workflow_exists": (root / WORKFLOW).exists(),
        "audit_script_exists": (root / AUDIT_SCRIPT).exists(),
        "capture_script_exists": (root / CAPTURE_SCRIPT).exists(),
        "verify_script_exists": (root / VERIFY_SCRIPT).exists(),
        "rr_doc_cites_register_id": RR_ID in rr_doc,
        "rr_doc_preserves_boundaries": "Billing launch authorised: false" in rr_doc and "Runtime KG" in rr_doc,
        "workflow_runs_verifier": "verify_rr011_live_billing_provider_integration.py" in workflow,
        "makefile_has_rr011_audit_target": "rr011-live-billing-provider-audit" in makefile,
        "makefile_has_rr011_check_target": "rr011-live-billing-provider-check" in makefile,
        "authority_audit_valid": audit_result.get("authority_valid") is True,
    }

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if audit_result.get("errors"):
        for error in audit_result["errors"]:
            if record.get("live_billing_provider_integration_recorded") is True or not error.startswith("missing final RR-011"):
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
        if record.get("live_billing_provider_integration_recorded") is True:
            for key in REQUIRED_TRUE_KEYS:
                if record.get(key) is not True:
                    errors.append(f"record flag must be true after evidence capture: {key}")
            if not isinstance(record.get("billing_provider_integration_audit"), dict):
                errors.append("billing_provider_integration_audit must be embedded after capture")
            if not record.get("billing_provider_integration_audit", {}).get("final_outputs_valid"):
                errors.append("billing_provider_integration_audit.final_outputs_valid must be true after capture")
        else:
            warnings.append("record is still pending evidence capture")
    else:
        errors.append("record JSON is missing")

    authority_errors = [
        err for err in errors
        if not err.startswith("record flag must be true")
        and err != "billing_provider_integration_audit must be embedded after capture"
        and err != "billing_provider_integration_audit.final_outputs_valid must be true after capture"
    ]
    authority_valid = not authority_errors
    valid = not errors and record.get("live_billing_provider_integration_recorded") is True

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "live_billing_provider_integration_recorded": record.get("live_billing_provider_integration_recorded") is True,
        "rr010_beta_outcome_reporting_valid": record.get("rr010_beta_outcome_reporting_valid") is True,
        "billing_provider_decision_recorded": record.get("billing_provider_decision_recorded") is True,
        "hosted_checkout_provider_attested": record.get("hosted_checkout_provider_attested") is True,
        "hosted_checkout_sandbox_validated": record.get("hosted_checkout_sandbox_validated") is True,
        "webhook_endpoint_validation_recorded": record.get("webhook_endpoint_validation_recorded") is True,
        "webhook_signature_validation_recorded": record.get("webhook_signature_validation_recorded") is True,
        "webhook_idempotency_validation_recorded": record.get("webhook_idempotency_validation_recorded") is True,
        "pricing_catalogue_approved": record.get("pricing_catalogue_approved") is True,
        "no_raw_card_storage_confirmed": record.get("no_raw_card_storage_confirmed") is True,
        "secrets_not_committed_confirmed": record.get("secrets_not_committed_confirmed") is True,
        "billing_launch_boundary_recorded": record.get("billing_launch_boundary_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr012_production_telemetry_remaining_visible": record.get("rr012_production_telemetry_remaining_visible") is True,
        "rr015_external_approvals_remaining_visible": record.get("rr015_external_approvals_remaining_visible") is True,
        "rr016_operational_drills_remaining_visible": record.get("rr016_operational_drills_remaining_visible") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised"),
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised"),
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
