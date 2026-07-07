#!/usr/bin/env python3
"""Verify PRD-0.5 test failure and collection stabilisation register."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.production_readiness.audit_prd005_test_failure_collection_stabilisation_register import audit


def evaluate(root: Path | str = Path(".")) -> dict:
    a = audit(Path(root))
    return {
        "valid": a["final_valid"],
        "authority_valid": a["authority_valid"],
        "prd_id": a["prd_id"],
        "errors": a["errors"],
        "warnings": a["warnings"],
        "test_failure_collection_stabilisation_register_recorded": a["recorded"],
        "prd004_test_dependency_bootstrap_baseline_valid": a["prd004_test_dependency_bootstrap_baseline_valid"],
        "test_inventory_recorded": a["test_inventory_recorded"],
        "collection_command_matrix_recorded": a["collection_command_matrix_recorded"],
        "failure_classification_schema_recorded": a["failure_classification_schema_recorded"],
        "triage_register_recorded": a["triage_register_recorded"],
        "test_file_count": a["test_file_count"],
        "test_function_count": a["test_function_count"],
        "collection_command_count": a["collection_command_count"],
        "triage_item_count": a["triage_item_count"],
        "no_test_deletions_authorised": a["no_test_deletions_authorised"],
        "workflow_hygiene_deferred_to_prd006": a["workflow_hygiene_deferred_to_prd006"],
        "runtime_kg_implementation_claimed": a["runtime_kg_implementation_claimed"],
        "runtime_kg_authority_switch_authorised": a["runtime_kg_authority_switch_authorised"],
        "authority_switch_executed": a["authority_switch_executed"],
        "production_release_authorised": a["production_release_authorised"],
        "deployment_authorised": a["deployment_authorised"],
        "release_tag_authorised": a["release_tag_authorised"],
        "public_beta_authorised": a["public_beta_authorised"],
        "public_beta_live_traffic_authorised": a["public_beta_live_traffic_authorised"],
        "live_learner_traffic_authorised": a["live_learner_traffic_authorised"],
        "billing_launch_authorised": a["billing_launch_authorised"],
        "live_payment_processing_authorised": a["live_payment_processing_authorised"],
        "new_kg_slice_authorised": a["new_kg_slice_authorised"],
        "prd1_implementation_authorised": a["prd1_implementation_authorised"],
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
        print(f"PRD-0.5 valid: {result['valid']}")
        print(f"PRD-0.5 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if (result["authority_valid"] if args.authority_only else result["valid"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
