"""Audit PRD-11.2R script taxonomy and functional overhaul."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.script_suites.script_taxonomy import evaluate_taxonomy

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-11.2R"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1102r_script_taxonomy_functional_overhaul_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_script_taxonomy_functional_overhaul.json"
REQUIRED_PATHS = [
    "scripts/script_suites/script_taxonomy.py",
    "scripts/script_suites/run_script_class.py",
    "scripts/script_suites/verify_script_taxonomy.py",
    "docs/testing/script_taxonomy.md",
    "docs/engineering/prd11_script_taxonomy_functional_overhaul.md",
    "docs/roadmap/production_readiness/script_taxonomy.json",
    "docs/roadmap/production_readiness/prd_1102r_script_taxonomy_functional_overhaul_record.json",
    "tests/unit/script_suites/test_script_taxonomy.py",
    "tests/unit/roadmap_reconciliation/test_prd1102r_script_taxonomy_functional_overhaul.py",
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
ALLOWED_NEXT = {"PRD-11.2R", "PRD-11.3R"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load(root / RECORD.relative_to(ROOT))
    register = _load(root / REGISTER.relative_to(ROOT))
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    prod_boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    taxonomy = evaluate_taxonomy(root)
    false_boundaries_locked = all(record.get(key) is False for key in FALSE_BOUNDARIES) and all(
        prod_boundaries.get(key) is False for key in FALSE_BOUNDARIES
    )
    register_next = register.get("next_authorised_item")
    prod_next = prod.get("next_authorised_item")
    evidence_recorded = record.get("script_taxonomy_evidence_recorded") is True
    authority_valid = all([
        not missing_paths,
        taxonomy.get("valid") is True,
        record.get("script_taxonomy_authority_recorded") is True,
        record.get("script_classes_recorded") is True,
        record.get("product_script_class_recorded") is True,
        record.get("runtime_script_class_recorded") is True,
        record.get("governance_script_class_recorded") is True,
        record.get("advisory_script_class_recorded") is True,
        record.get("functional_roles_recorded") is True,
        record.get("script_mutability_policy_recorded") is True,
        record.get("governance_script_freshness_gate_recorded") is True,
        record.get("script_outputs_cannot_self_prove_release_readiness") is True,
        false_boundaries_locked,
        register_next in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
        register_next == prod_next,
    ])
    valid = all([
        authority_valid,
        evidence_recorded,
        record.get("prd113r_handoff_authorised") is True,
        record.get("next_authorised_item") == "PRD-11.3R",
        register_next == "PRD-11.3R",
        prod_next == "PRD-11.3R",
        (root / SUMMARY.relative_to(ROOT)).exists(),
    ])
    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "missing_paths": missing_paths,
        "taxonomy_valid": taxonomy.get("valid") is True,
        "script_taxonomy_authority_recorded": record.get("script_taxonomy_authority_recorded") is True,
        "script_taxonomy_evidence_recorded": evidence_recorded,
        "script_classes_recorded": record.get("script_classes_recorded") is True,
        "product_script_class_recorded": record.get("product_script_class_recorded") is True,
        "runtime_script_class_recorded": record.get("runtime_script_class_recorded") is True,
        "governance_script_class_recorded": record.get("governance_script_class_recorded") is True,
        "advisory_script_class_recorded": record.get("advisory_script_class_recorded") is True,
        "functional_roles_recorded": record.get("functional_roles_recorded") is True,
        "script_mutability_policy_recorded": record.get("script_mutability_policy_recorded") is True,
        "governance_script_freshness_gate_recorded": record.get("governance_script_freshness_gate_recorded") is True,
        "script_outputs_cannot_self_prove_release_readiness": record.get("script_outputs_cannot_self_prove_release_readiness") is True,
        "false_boundaries_locked": false_boundaries_locked,
        "prd113r_handoff_authorised": record.get("prd113r_handoff_authorised") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register_next,
        "production_register_next_authorised_item": prod_next,
        "taxonomy": taxonomy,
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
