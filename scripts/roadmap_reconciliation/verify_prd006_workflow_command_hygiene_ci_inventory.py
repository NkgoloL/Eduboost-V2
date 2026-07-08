#!/usr/bin/env python3
"""Verify PRD-0.6 workflow command hygiene and CI inventory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.production_readiness.audit_prd006_workflow_command_hygiene_ci_inventory import audit


def evaluate(root: Path | str = Path(".")) -> dict:
    a = audit(Path(root))
    return {
        "valid": a["final_valid"],
        "authority_valid": a["authority_valid"],
        "prd_id": a["prd_id"],
        "errors": a["errors"],
        "warnings": a["warnings"],
        "workflow_command_hygiene_ci_inventory_recorded": a["recorded"],
        "prd005_test_failure_collection_stabilisation_register_valid": a["prd005_test_failure_collection_stabilisation_register_valid"],
        "workflow_inventory_recorded": a["workflow_inventory_recorded"],
        "ci_workflow_inventory_recorded": a["ci_workflow_inventory_recorded"],
        "workflow_count": a["workflow_count"],
        "direct_pytest_command_count": a["direct_pytest_command_count"],
        "direct_pytest_workflow_count": a["direct_pytest_workflow_count"],
        "module_pytest_command_count": a["module_pytest_command_count"],
        "module_pytest_workflow_count": a["module_pytest_workflow_count"],
        "requirements_dev_install_workflow_count": a["requirements_dev_install_workflow_count"],
        "pytest_workflow_missing_dev_install_count": a["pytest_workflow_missing_dev_install_count"],
        "direct_pytest_commands_resolved": a["direct_pytest_commands_resolved"],
        "canonical_pytest_command_recorded": a["canonical_pytest_command_recorded"],
        "openapi_generated_artifact_canonicalisation_deferred_to_prd007": a["openapi_generated_artifact_canonicalisation_deferred_to_prd007"],
        "branch_release_naming_reconciliation_deferred_to_prd008": a["branch_release_naming_reconciliation_deferred_to_prd008"],
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
        print(f"PRD-0.6 valid: {result['valid']}")
        print(f"PRD-0.6 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if (result["authority_valid"] if args.authority_only else result["valid"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
