#!/usr/bin/env python3
"""Verify final roadmap reconciliation closure authority and captured evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ITEMS = [
    ("RR-001", "Roadmap/status reconciliation", "rr_001_atlas_phase_status_record.json", "atlas_phase_register_reconciled"),
    ("RR-002", "Privacy / POPIA completion", "rr_002_privacy_popia_completion_record.json", "privacy_popia_completion_recorded"),
    ("RR-003", "Coverage / CI / route authority", "rr_003_coverage_ci_route_authority_record.json", "coverage_ci_route_authority_recorded"),
    ("RR-004", "Workspace hygiene", "rr_004_workspace_hygiene_record.json", "workspace_hygiene_recorded"),
    ("RR-005", "Technical debt burn-down", "rr_005_technical_debt_burndown_record.json", "technical_debt_burndown_recorded"),
    ("RR-006", "Security posture deepening", "rr_006_security_posture_deepening_record.json", "security_posture_deepening_recorded"),
    ("RR-007", "Product completeness / quality gates", "rr_007_product_quality_gates_record.json", "product_quality_gates_recorded"),
    ("RR-008", "Operational readiness", "rr_008_operational_readiness_record.json", "operational_readiness_recorded"),
    ("RR-009", "Governance / process reconciliation", "rr_009_governance_process_reconciliation_record.json", "governance_process_reconciliation_recorded"),
    ("RR-010", "Beta outcome reporting", "rr_010_beta_outcome_reporting_record.json", "beta_outcome_reporting_recorded"),
    ("RR-011", "Live billing provider integration", "rr_011_live_billing_provider_integration_record.json", "live_billing_provider_integration_recorded"),
    ("RR-012", "Production telemetry dashboard implementation", "rr_012_production_telemetry_dashboard_record.json", "production_telemetry_dashboard_recorded"),
    ("RR-013", "Advanced mastery-model research", "rr_013_advanced_mastery_model_research_record.json", "advanced_mastery_model_research_recorded"),
    ("RR-014", "Public beta expansion", "rr_014_public_beta_expansion_record.json", "public_beta_expansion_readiness_recorded"),
    ("RR-015", "External approvals", "rr_015_external_approvals_record.json", "external_approvals_recorded"),
    ("RR-016", "Operational drills", "rr_016_operational_drills_record.json", "operational_drills_recorded"),
    ("RR-017", "Release safety controls", "rr_017_release_safety_controls_record.json", "release_safety_controls_recorded"),
    ("RR-018", "Trustworthy beta product quality", "rr_018_trustworthy_beta_product_quality_record.json", "trustworthy_beta_product_quality_recorded"),
]

RECON_DIR = Path("docs/roadmap/reconciliation")
REGISTER = RECON_DIR / "outstanding_work_register.md"
MATRIX = RECON_DIR / "final_roadmap_reconciliation_closure_matrix.json"
REPORT = RECON_DIR / "final_roadmap_reconciliation_closure.md"
RECORD = RECON_DIR / "final_roadmap_reconciliation_closure_record.json"

BOUNDARY_FALSE_KEYS = [
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "runtime_kg_implementation_claimed",
    "new_unreconciled_work_authorised",
    "new_rr_items_introduced",
]

REQUIRED_TRUE_AFTER_CAPTURE = [
    "final_roadmap_reconciliation_closure_recorded",
    "all_reconciled_rr_items_addressed",
    "all_reconciled_rr_items_addressed_through_rr018",
    "outstanding_work_register_closed_through_rr018",
    "final_closure_report_recorded",
    "final_closure_matrix_recorded",
    "rr003_fallback_coverage_caveat_visible",
    "rr006_non_required_checks_caveat_visible",
    "rr016_clean_git_state_caveat_visible",
]


def _json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)

    def p(path: Path) -> Path:
        return root / path

    errors: list[str] = []
    warnings: list[str] = []
    rr_results: list[dict[str, Any]] = []

    register_text = _text(p(REGISTER))
    report_text = _text(p(REPORT))
    matrix = _json(p(MATRIX))
    closure_record = _json(p(RECORD))
    rr018 = _json(p(RECON_DIR / "rr_018_trustworthy_beta_product_quality_record.json"))

    if not REGISTER.exists() and not p(REGISTER).exists():
        errors.append("outstanding_work_register.md is missing")
    for rr_id, title, filename, required_flag in RR_ITEMS:
        record_path = p(RECON_DIR / filename)
        record = _json(record_path)
        ok = bool(record) and record.get("rr_id") == rr_id and record.get(required_flag) is True
        boundary_ok = all(record.get(key) is False for key in BOUNDARY_FALSE_KEYS if key in record)
        rr_results.append({
            "rr_id": rr_id,
            "title": title,
            "record_path": str(RECON_DIR / filename),
            "required_flag": required_flag,
            "required_flag_present": record.get(required_flag) is True,
            "rr_id_valid": record.get("rr_id") == rr_id,
            "boundary_ok": boundary_ok,
            "addressed": ok and boundary_ok,
        })
        if rr_id not in register_text:
            errors.append(f"register must still cite {rr_id}")
        if not record:
            errors.append(f"missing record for {rr_id}: {record_path}")
        elif record.get("rr_id") != rr_id:
            errors.append(f"{filename} rr_id must be {rr_id}")
        elif record.get(required_flag) is not True:
            errors.append(f"{rr_id} completion flag must be true: {required_flag}")
        if not boundary_ok:
            errors.append(f"{rr_id} has an authorised boundary flag that must remain false")

    authority_checks = {
        "report_exists": p(REPORT).exists(),
        "matrix_exists": p(MATRIX).exists(),
        "record_exists": p(RECORD).exists(),
        "register_has_rr001_to_rr018": all(rr_id in register_text for rr_id, *_ in RR_ITEMS),
        "matrix_has_18_items": matrix.get("rr_count") == 18 and len(matrix.get("items", [])) == 18,
        "report_says_not_rr019": "not be treated as `RR-019`" in report_text,
        "report_preserves_boundaries": "Production release authorised: false" in report_text and "Runtime KG implementation claimed: false" in report_text,
        "rr018_all_items_flag": rr018.get("all_reconciled_rr_items_addressed_through_rr018") is True,
    }
    for key, ok in authority_checks.items():
        if not ok:
            errors.append(f"authority check failed: {key}")

    final_recorded = closure_record.get("final_roadmap_reconciliation_closure_recorded") is True
    if final_recorded:
        for key in REQUIRED_TRUE_AFTER_CAPTURE:
            if closure_record.get(key) is not True:
                errors.append(f"closure record flag must be true after capture: {key}")
    else:
        warnings.append("final roadmap closure record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if closure_record.get(key) is not False:
            errors.append(f"closure boundary flag must remain false: {key}")

    all_rr_addressed = all(item["addressed"] for item in rr_results)
    authority_valid = all(authority_checks.values()) and all_rr_addressed and not [e for e in errors if not e.startswith("closure record flag") and not e.startswith("closure boundary")]
    valid = authority_valid and final_recorded and not errors

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "closure_id": "FINAL-ROADMAP-RECONCILIATION-CLOSURE",
        "record_path": str(RECORD),
        "errors": errors,
        "warnings": warnings,
        "rr_results": rr_results,
        "all_reconciled_rr_items_addressed": all_rr_addressed,
        "all_reconciled_rr_items_addressed_through_rr018": rr018.get("all_reconciled_rr_items_addressed_through_rr018") is True,
        "final_roadmap_reconciliation_closure_recorded": final_recorded,
        "outstanding_work_register_closed_through_rr018": closure_record.get("outstanding_work_register_closed_through_rr018") is True,
        "rr003_fallback_coverage_caveat_visible": closure_record.get("rr003_fallback_coverage_caveat_visible") is True,
        "rr006_non_required_checks_caveat_visible": closure_record.get("rr006_non_required_checks_caveat_visible") is True,
        "rr016_clean_git_state_caveat_visible": closure_record.get("rr016_clean_git_state_caveat_visible") is True,
        "new_rr_items_introduced": closure_record.get("new_rr_items_introduced") is True,
        "new_unreconciled_work_authorised": closure_record.get("new_unreconciled_work_authorised") is True,
        "production_release_authorised": closure_record.get("production_release_authorised") is True,
        "deployment_authorised": closure_record.get("deployment_authorised") is True,
        "release_tag_authorised": closure_record.get("release_tag_authorised") is True,
        "public_beta_authorised": closure_record.get("public_beta_authorised") is True,
        "runtime_kg_implementation_claimed": closure_record.get("runtime_kg_implementation_claimed") is True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-only", action="store_true", help="Pass if authority is valid even before closure evidence capture.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path("."))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]).lower())
    ok = result["authority_valid"] if args.authority_only else result["valid"]
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
