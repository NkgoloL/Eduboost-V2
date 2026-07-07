#!/usr/bin/env python3
"""Verify PRD-0.4 test/dependency bootstrap baseline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from scripts.production_readiness.audit_prd004_test_dependency_bootstrap_baseline import audit

def evaluate(root: Path | str = Path(".")) -> dict:
    a = audit(Path(root))
    return {"valid": a["final_valid"], "authority_valid": a["authority_valid"], "prd_id": a["prd_id"], "errors": a["errors"], "warnings": a["warnings"], "test_dependency_bootstrap_baseline_recorded": a["recorded"], "prd003_documentation_housekeeping_ratchet_refresh_valid": a["prd003_documentation_housekeeping_ratchet_refresh_valid"], "dependency_manifest_recorded": a["dependency_manifest_recorded"], "bootstrap_command_contract_recorded": a["bootstrap_command_contract_recorded"], "python_test_dependency_contract_recorded": a["python_test_dependency_contract_recorded"], "frontend_test_dependency_contract_recorded": a["frontend_test_dependency_contract_recorded"], "ci_dependency_install_contract_recorded": a["ci_dependency_install_contract_recorded"], "deferred_failure_triage_boundary_recorded": a["deferred_failure_triage_boundary_recorded"], "requirements_file_count": a["requirements_file_count"], "pytest_declared": a["pytest_declared"], "pytest_cov_declared": a["pytest_cov_declared"], "frontend_vitest_declared": a["frontend_vitest_declared"], "workflow_count": a["workflow_count"], "direct_pytest_workflow_count": a["direct_pytest_workflow_count"], "module_pytest_workflow_count": a["module_pytest_workflow_count"], "runtime_kg_implementation_claimed": a["runtime_kg_implementation_claimed"], "runtime_kg_authority_switch_authorised": a["runtime_kg_authority_switch_authorised"], "authority_switch_executed": a["authority_switch_executed"], "production_release_authorised": a["production_release_authorised"], "deployment_authorised": a["deployment_authorised"], "release_tag_authorised": a["release_tag_authorised"], "public_beta_authorised": a["public_beta_authorised"], "public_beta_live_traffic_authorised": a["public_beta_live_traffic_authorised"], "live_learner_traffic_authorised": a["live_learner_traffic_authorised"], "billing_launch_authorised": a["billing_launch_authorised"], "live_payment_processing_authorised": a["live_payment_processing_authorised"], "new_kg_slice_authorised": a["new_kg_slice_authorised"], "prd1_implementation_authorised": a["prd1_implementation_authorised"]}

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
        print(f"PRD-0.4 valid: {result['valid']}")
        print(f"PRD-0.4 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if (result["authority_valid"] if args.authority_only else result["valid"]) else 1

if __name__ == "__main__":
    raise SystemExit(main())
