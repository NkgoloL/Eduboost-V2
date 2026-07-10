"""Audit PRD-11.3R coverage alignment and documentation-defined closure."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.coverage_suites.coverage_contract import evaluate_coverage_contract

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.3R"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1103r_coverage_alignment_documentation_defined_closure_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_coverage_alignment_documentation_defined_closure.json"
REQUIRED_PATHS = [
    "scripts/coverage_suites/coverage_contract.py",
    "scripts/coverage_suites/run_coverage_domain.py",
    "scripts/coverage_suites/verify_coverage_contract.py",
    "docs/testing/documentation_defined_coverage.md",
    "docs/testing/coverage_quality_threshold_contract.md",
    "docs/engineering/prd11_coverage_alignment_documentation_defined_coverage_closure.md",
    "docs/roadmap/production_readiness/coverage_contract.json",
    "docs/roadmap/production_readiness/prd_1103r_coverage_alignment_documentation_defined_closure_record.json",
    "tests/unit/coverage_suites/test_coverage_contract.py",
    "tests/unit/roadmap_reconciliation/test_prd1103r_coverage_alignment_documentation_defined_closure.py",
]
FALSE_BOUNDARIES = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-11.3R", "PRD-11.0R.RUNTIME-RESTORE"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / RECORD.relative_to(ROOT))
    register = _load(root / REGISTER.relative_to(ROOT))
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    coverage = evaluate_coverage_contract(root)
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    false_boundaries_locked = all(record.get(key) is False for key in FALSE_BOUNDARIES) and all(prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES)
    evidence_recorded = record.get("coverage_alignment_evidence_recorded") is True
    authority_valid = all([
        not missing_paths,
        coverage.get("valid") is True,
        record.get("coverage_alignment_authority_recorded") is True,
        record.get("documentation_defined_coverage_contract_recorded") is True,
        record.get("product_coverage_class_recorded") is True,
        record.get("runtime_coverage_class_recorded") is True,
        record.get("governance_coverage_class_recorded") is True,
        record.get("advisory_coverage_class_recorded") is True,
        record.get("coverage_thresholds_aligned_to_documentation") is True,
        record.get("coverage_failure_exit_state_preserved") is True,
        record.get("presence_only_coverage_evidence_forbidden") is True,
        record.get("negative_path_coverage_required") is True,
        false_boundaries_locked,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    valid = all([
        authority_valid,
        evidence_recorded,
        record.get("runtime_restore_handoff_authorised") is True,
        record.get("next_authorised_item") == "PRD-11.0R.RUNTIME-RESTORE",
        register_next == "PRD-11.0R.RUNTIME-RESTORE",
        prod_next == "PRD-11.0R.RUNTIME-RESTORE",
        (root / SUMMARY.relative_to(ROOT)).exists(),
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "coverage_contract_valid": coverage.get("valid") is True,
        "coverage_alignment_authority_recorded": record.get("coverage_alignment_authority_recorded") is True,
        "coverage_alignment_evidence_recorded": evidence_recorded,
        "documentation_defined_coverage_contract_recorded": record.get("documentation_defined_coverage_contract_recorded") is True,
        "product_coverage_class_recorded": record.get("product_coverage_class_recorded") is True,
        "runtime_coverage_class_recorded": record.get("runtime_coverage_class_recorded") is True,
        "governance_coverage_class_recorded": record.get("governance_coverage_class_recorded") is True,
        "advisory_coverage_class_recorded": record.get("advisory_coverage_class_recorded") is True,
        "coverage_thresholds_aligned_to_documentation": record.get("coverage_thresholds_aligned_to_documentation") is True,
        "coverage_failure_exit_state_preserved": record.get("coverage_failure_exit_state_preserved") is True,
        "presence_only_coverage_evidence_forbidden": record.get("presence_only_coverage_evidence_forbidden") is True,
        "negative_path_coverage_required": record.get("negative_path_coverage_required") is True,
        "runtime_restore_handoff_authorised": record.get("runtime_restore_handoff_authorised") is True,
        "false_boundaries_locked": false_boundaries_locked,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register_next,
        "production_register_next_authorised_item": prod_next,
        "coverage_contract": coverage,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(ROOT)
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    raise SystemExit(0 if (result.get("authority_valid") if args.authority_only else result.get("valid")) else 1)
