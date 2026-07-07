#!/usr/bin/env python3
"""Verify PRD-0.1 canonical current-state documentation refresh."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd001_canonical_current_state_documentation_refresh import RECORD, audit

PRD_ID = "PRD-0.1"

def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    audit_result = audit(Path(root))
    return {
        "valid": audit_result["final_valid"],
        "authority_valid": audit_result["authority_valid"],
        "prd_id": PRD_ID,
        "record_path": str(RECORD),
        "errors": audit_result["errors"],
        "warnings": audit_result["warnings"],
        "canonical_current_state_documentation_refresh_recorded": audit_result["recorded"],
        "prd000_production_readiness_stream_authority_valid": audit_result["prd000_production_readiness_stream_authority_valid"],
        "truth_map_recorded": audit_result["truth_map_recorded"],
        "canonical_docs_refreshed": audit_result["canonical_docs_refreshed"],
        "stale_canonical_claims_removed": audit_result["stale_canonical_claims_removed"],
        "runtime_kg_implementation_claimed": audit_result["runtime_kg_implementation_claimed"],
        "runtime_kg_authority_switch_authorised": audit_result["runtime_kg_authority_switch_authorised"],
        "authority_switch_executed": audit_result["authority_switch_executed"],
        "production_release_authorised": audit_result["production_release_authorised"],
        "deployment_authorised": audit_result["deployment_authorised"],
        "release_tag_authorised": audit_result["release_tag_authorised"],
        "public_beta_authorised": audit_result["public_beta_authorised"],
        "public_beta_live_traffic_authorised": audit_result["public_beta_live_traffic_authorised"],
        "live_learner_traffic_authorised": audit_result["live_learner_traffic_authorised"],
        "billing_launch_authorised": audit_result["billing_launch_authorised"],
        "live_payment_processing_authorised": audit_result["live_payment_processing_authorised"],
        "new_kg_slice_authorised": audit_result["new_kg_slice_authorised"],
        "prd1_implementation_authorised": audit_result["prd1_implementation_authorised"],
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
        print(f"PRD-0.1 valid: {result['valid']}")
        print(f"PRD-0.1 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
