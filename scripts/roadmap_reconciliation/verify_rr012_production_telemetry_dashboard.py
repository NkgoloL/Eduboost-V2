#!/usr/bin/env python3
"""Verify RR-012 production telemetry dashboard implementation authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.telemetry.audit_rr012_production_telemetry_dashboard import audit

RR_ID = "RR-012"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR011_RECORD = Path("docs/roadmap/reconciliation/rr_011_live_billing_provider_integration_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard.md")
WORKFLOW = Path(".github/workflows/rr012-production-telemetry-dashboard.yml")
AUDIT_SCRIPT = Path("scripts/telemetry/audit_rr012_production_telemetry_dashboard.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr012_production_telemetry_dashboard_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr012_production_telemetry_dashboard.py")
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
    "production_telemetry_dashboard_recorded",
    "rr011_live_billing_provider_integration_valid",
    "dashboard_implementation_attested",
    "grafana_dashboard_inventory_recorded",
    "production_api_dashboard_implemented",
    "learner_journey_dashboard_implemented",
    "popia_privacy_dashboard_implemented",
    "ai_llm_dashboard_implemented",
    "billing_operations_dashboard_implemented",
    "infrastructure_readiness_dashboard_implemented",
    "slo_dashboard_validation_recorded",
    "alert_routing_validation_recorded",
    "dashboard_privacy_boundary_recorded",
    "no_learner_pii_exposed",
    "secrets_not_committed_confirmed",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr013_mastery_model_research_remaining_visible",
    "rr015_external_approvals_remaining_visible",
    "rr016_operational_drills_remaining_visible",
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
        "rr011_record": RR011_RECORD,
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
            errors.append(f"missing required RR-012 file: {path}")

    register = _read(root, REGISTER)
    checks["register_mentions_rr012"] = "RR-012" in register and "Production telemetry dashboard implementation" in register
    if not checks["register_mentions_rr012"]:
        errors.append("outstanding work register must mention RR-012 production telemetry dashboard implementation")

    rr011 = _json(root, RR011_RECORD)
    checks["rr011_record_valid"] = rr011.get("live_billing_provider_integration_recorded") is True
    if not checks["rr011_record_valid"]:
        errors.append("RR-011 live billing provider integration must be recorded before RR-012")

    makefile = _read(root, MAKEFILE)
    for target in ("rr012-production-telemetry-dashboard-audit", "rr012-production-telemetry-dashboard-check"):
        ok = target in makefile
        checks[f"makefile_target:{target}"] = ok
        if not ok:
            errors.append(f"Makefile missing target: {target}")

    workflow = _read(root, WORKFLOW)
    checks["workflow_mentions_rr012"] = "RR-012 Production Telemetry Dashboard" in workflow
    if not checks["workflow_mentions_rr012"]:
        errors.append("RR-012 workflow must identify the RR-012 check")

    audit_result = audit(root, require_final=False)
    checks["authority_audit_valid"] = audit_result.get("authority_valid") is True
    if not checks["authority_audit_valid"]:
        errors.extend(audit_result.get("errors", []))

    record = _json(root, RECORD)
    if record.get("__json_error__"):
        errors.append(f"RR-012 record JSON invalid: {record['__json_error__']}")
        record = {}
    checks["record_rr_id"] = record.get("rr_id") == RR_ID
    if record and record.get("rr_id") != RR_ID:
        errors.append("RR-012 record must carry rr_id=RR-012")

    authority_valid = not errors

    for key in BOUNDARY_FALSE_KEYS:
        value = record.get(key)
        checks[f"boundary_false:{key}"] = value is False
        if record and value is not False:
            errors.append(f"RR-012 boundary key must remain false: {key}")

    for key in REQUIRED_TRUE_KEYS:
        checks[f"record_true:{key}"] = record.get(key) is True
        if record and record.get("production_telemetry_dashboard_recorded") is True and record.get(key) is not True:
            errors.append(f"RR-012 recorded evidence missing true flag: {key}")

    if record and record.get("production_telemetry_dashboard_recorded") is not True:
        warnings.append("record is still pending evidence capture")

    final_audit = None
    if record.get("production_telemetry_dashboard_recorded") is True:
        final_audit = audit(root, require_final=True)
        checks["final_audit_valid"] = final_audit.get("valid") is True
        if not final_audit.get("valid"):
            errors.extend(final_audit.get("errors", []))
        embedded = record.get("production_telemetry_dashboard_audit", {})
        checks["record_embeds_valid_audit"] = isinstance(embedded, dict) and embedded.get("valid") is True
        if not checks["record_embeds_valid_audit"]:
            errors.append("RR-012 record must embed a valid production telemetry dashboard audit")

    valid = authority_valid and record.get("production_telemetry_dashboard_recorded") is True and not errors
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "production_telemetry_dashboard_recorded": record.get("production_telemetry_dashboard_recorded") is True,
        "rr011_live_billing_provider_integration_valid": record.get("rr011_live_billing_provider_integration_valid") is True,
        "dashboard_implementation_attested": record.get("dashboard_implementation_attested") is True,
        "grafana_dashboard_inventory_recorded": record.get("grafana_dashboard_inventory_recorded") is True,
        "production_api_dashboard_implemented": record.get("production_api_dashboard_implemented") is True,
        "learner_journey_dashboard_implemented": record.get("learner_journey_dashboard_implemented") is True,
        "popia_privacy_dashboard_implemented": record.get("popia_privacy_dashboard_implemented") is True,
        "ai_llm_dashboard_implemented": record.get("ai_llm_dashboard_implemented") is True,
        "billing_operations_dashboard_implemented": record.get("billing_operations_dashboard_implemented") is True,
        "infrastructure_readiness_dashboard_implemented": record.get("infrastructure_readiness_dashboard_implemented") is True,
        "slo_dashboard_validation_recorded": record.get("slo_dashboard_validation_recorded") is True,
        "alert_routing_validation_recorded": record.get("alert_routing_validation_recorded") is True,
        "dashboard_privacy_boundary_recorded": record.get("dashboard_privacy_boundary_recorded") is True,
        "no_learner_pii_exposed": record.get("no_learner_pii_exposed") is True,
        "secrets_not_committed_confirmed": record.get("secrets_not_committed_confirmed") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr013_mastery_model_research_remaining_visible": record.get("rr013_mastery_model_research_remaining_visible") is True,
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
