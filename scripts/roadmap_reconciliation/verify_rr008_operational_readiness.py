#!/usr/bin/env python3
"""Verify RR-008 operational readiness authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-008"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR007_RECORD = Path("docs/roadmap/reconciliation/rr_007_product_quality_gates_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_008_operational_readiness_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_008_operational_readiness.md")
POLICY = Path("docs/operations/readiness/rr008_operational_readiness_policy.md")
INCIDENT_DOC = Path("docs/operations/readiness/rr008_incident_response_runbook_index.md")
SLO_DOC = Path("docs/operations/readiness/rr008_slo_definitions.md")
CAPACITY_DOC = Path("docs/operations/readiness/rr008_capacity_planning.md")
LLM_COST_DOC = Path("docs/operations/readiness/rr008_llm_cost_model.md")
GRAFANA_DOC = Path("docs/operations/readiness/rr008_grafana_alert_linkage.md")
MANIFEST = Path("docs/operations/readiness/rr008_operational_readiness_manifest.json")
WORKFLOW = Path(".github/workflows/rr008-operational-readiness.yml")
AUDIT_SCRIPT = Path("scripts/operations_readiness/audit_rr008_operational_readiness.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr008_operational_readiness_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr008_operational_readiness.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_KEYS = (
    "operational_readiness_recorded",
    "incident_response_runbook_recorded",
    "slo_definitions_recorded",
    "capacity_planning_recorded",
    "llm_cost_model_recorded",
    "grafana_alert_linkage_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr016_drills_remaining_visible",
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
    rr007_record = _json(root, RR007_RECORD)
    record = _json(root, RECORD)
    manifest = _json(root, MANIFEST)
    rr_doc = _read(root, RR_DOC)
    policy = _read(root, POLICY)
    incident_doc = _read(root, INCIDENT_DOC)
    slo_doc = _read(root, SLO_DOC)
    capacity_doc = _read(root, CAPACITY_DOC)
    llm_doc = _read(root, LLM_COST_DOC)
    grafana_doc = _read(root, GRAFANA_DOC)
    workflow = _read(root, WORKFLOW)
    audit_script = _read(root, AUDIT_SCRIPT)
    makefile = _read(root, MAKEFILE)

    checks = {
        "rr008_in_outstanding_register": RR_ID in register and "Operational readiness" in register,
        "rr007_predecessor_recorded": rr007_record.get("product_quality_gates_recorded") is True,
        "rr_doc_exists": (root / RR_DOC).exists(),
        "record_exists": (root / RECORD).exists(),
        "manifest_exists": (root / MANIFEST).exists(),
        "policy_exists": (root / POLICY).exists(),
        "incident_doc_exists": (root / INCIDENT_DOC).exists(),
        "slo_doc_exists": (root / SLO_DOC).exists(),
        "capacity_doc_exists": (root / CAPACITY_DOC).exists(),
        "llm_cost_doc_exists": (root / LLM_COST_DOC).exists(),
        "grafana_doc_exists": (root / GRAFANA_DOC).exists(),
        "workflow_exists": (root / WORKFLOW).exists(),
        "audit_script_exists": (root / AUDIT_SCRIPT).exists(),
        "capture_script_exists": (root / CAPTURE_SCRIPT).exists(),
        "verify_script_exists": (root / VERIFY_SCRIPT).exists(),
        "rr_doc_cites_register_id": RR_ID in rr_doc,
        "policy_mentions_rr003_caveat": "RR-003" in policy and "0.0" in policy,
        "policy_mentions_rr006_caveat": "RR-006" in policy and "non-required" in policy,
        "policy_preserves_boundaries": "Runtime KG" in policy and "not authorised" in policy,
        "policy_distinguishes_rr016_drills": "RR-016" in policy and "drill" in policy.lower(),
        "incident_doc_has_marker": "Incident response runbook index recorded: true" in incident_doc,
        "slo_doc_has_marker": "SLO definitions recorded: true" in slo_doc,
        "capacity_doc_has_marker": "Capacity planning recorded: true" in capacity_doc,
        "llm_cost_doc_has_marker": "LLM cost model recorded: true" in llm_doc,
        "grafana_doc_has_marker": "Grafana alert linkage recorded: true" in grafana_doc,
        "workflow_runs_verifier": "verify_rr008_operational_readiness.py" in workflow,
        "audit_script_checks_all_gate_areas": all(
            token in audit_script
            for token in (
                "incident_response_runbook_recorded",
                "slo_definitions_recorded",
                "capacity_planning_recorded",
                "llm_cost_model_recorded",
                "grafana_alert_linkage_recorded",
            )
        ),
        "makefile_has_rr008_audit_target": "rr008-operational-readiness-audit" in makefile,
        "makefile_has_rr008_check_target": "rr008-operational-readiness-check" in makefile,
    }

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if manifest.get("__json_error__"):
        errors.append(f"manifest JSON invalid: {manifest['__json_error__']}")
    elif manifest:
        for key in (
            "incident_response_runbook_recorded",
            "slo_definitions_recorded",
            "capacity_planning_recorded",
            "llm_cost_model_recorded",
            "grafana_alert_linkage_recorded",
        ):
            if manifest.get(key) is not True:
                errors.append(f"manifest flag must be true: {key}")
        for key in BOUNDARY_FALSE_KEYS:
            if manifest.get(key) is not False:
                errors.append(f"manifest boundary flag must be false: {key}")
    else:
        errors.append("RR-008 operational readiness manifest is missing")

    if record.get("__json_error__"):
        errors.append(f"record JSON invalid: {record['__json_error__']}")
    elif record:
        if record.get("rr_id") != RR_ID:
            errors.append(f"record rr_id must be {RR_ID}")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"boundary flag must remain false: {key}")
        if record.get("operational_readiness_recorded") is True:
            for key in REQUIRED_TRUE_KEYS:
                if record.get(key) is not True:
                    errors.append(f"record flag must be true after evidence capture: {key}")
            if not isinstance(record.get("operational_readiness_audit"), dict):
                errors.append("operational_readiness_audit must be embedded after capture")
        else:
            warnings.append("record is still pending evidence capture")
    else:
        errors.append("record JSON is missing")

    authority_errors = [
        err for err in errors
        if not err.startswith("record flag must be true")
        and err != "operational_readiness_audit must be embedded after capture"
    ]
    authority_valid = not authority_errors
    valid = not errors and record.get("operational_readiness_recorded") is True

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "operational_readiness_recorded": record.get("operational_readiness_recorded") is True,
        "incident_response_runbook_recorded": record.get("incident_response_runbook_recorded") is True,
        "slo_definitions_recorded": record.get("slo_definitions_recorded") is True,
        "capacity_planning_recorded": record.get("capacity_planning_recorded") is True,
        "llm_cost_model_recorded": record.get("llm_cost_model_recorded") is True,
        "grafana_alert_linkage_recorded": record.get("grafana_alert_linkage_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr016_drills_remaining_visible": record.get("rr016_drills_remaining_visible") is True,
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
