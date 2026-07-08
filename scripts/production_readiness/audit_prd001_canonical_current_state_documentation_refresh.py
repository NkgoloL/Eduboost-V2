#!/usr/bin/env python3
"""Audit PRD-0.1 canonical current-state documentation refresh."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd000_production_readiness_stream_authority import evaluate as evaluate_prd000

PRD000_RECORD = Path("docs/roadmap/production_readiness/prd_000_production_readiness_stream_authority_record.json")

PRD_ID = "PRD-0.1"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_001_canonical_current_state_documentation_refresh.md"
TRUTH_MAP = ROOT / "current_state_documentation_truth_map.json"
RECORD = ROOT / "prd_001_canonical_current_state_documentation_refresh_record.json"
CANONICAL_DOCS = [Path("docs/current_state.md"), Path("README.md"), Path("docs/README.md"), Path("docs/roadmap/README.md"), Path("docs/architecture/README.md")]
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]
REQUIRED_PHRASES = ["RR roadmap/TODO register: closed", "KG roadmap: closed through KG-8", "Controlled runtime KG authority switch: executed", "Production-readiness stream: open", "Current authorised item: PRD-0.1", "PRD-1 implementation: blocked until PRD-0.10 closure", "production_release_authorised: false", "deployment_authorised: false", "public_beta_authorised: false", "billing_launch_authorised: false", "live_payment_processing_authorised: false", "new_kg_slice_authorised: false"]
FORBIDDEN_PHRASES = ["RR-010 beta outcome reporting, RR-015 external approvals, RR-016 operational drills, and RR-017 release safety controls remain outstanding", "runtime KG implementation remain unauthorised", "runtime KG implementation remains unauthorised", "Next after KG-0: `KG-1 — CAPS graph foundation`", "New roadmap or product work remains blocked unless reconciled into the RR register"]

def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    def p(path: Path) -> Path:
        return root / path
    prd000 = evaluate_prd000(root)
    prd000_record = read_json(p(PRD000_RECORD))
    prd000_record_valid = (
        prd000_record.get("production_readiness_stream_authority_recorded") is True
        and prd000_record.get("verification", {}).get("valid") is True
    )
    prd000_valid = prd000.get("valid") is True or prd000_record_valid
    if not prd000_valid:
        errors.append("PRD-0.0 production-readiness stream authority verifier or captured record must be valid")
    register = read_json(p(REGISTER))
    truth_map = read_json(p(TRUTH_MAP))
    record = read_json(p(RECORD))
    for path in [REGISTER, PRD_DOC, TRUTH_MAP, RECORD, *CANONICAL_DOCS]:
        if not p(path).exists():
            errors.append(f"missing PRD-0.1 file: {path}")
    if register.get("stream_id") != "PRD-PRODUCTION-READINESS":
        errors.append("production readiness register must identify PRD-PRODUCTION-READINESS")
    ALLOWED_LAST_RECORDED_ITEMS = {f"PRD-0.{idx}" for idx in range(0, 11)} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    ALLOWED_NEXT_AUTHORISED_ITEMS = {f"PRD-0.{idx}" for idx in range(1, 11)} | {"PRD-1"} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    if register.get("last_recorded_item") not in ALLOWED_LAST_RECORDED_ITEMS:
        errors.append("production readiness register last_recorded_item must be a valid PRD-0.x state")
    if register.get("next_authorised_item") not in ALLOWED_NEXT_AUTHORISED_ITEMS:
        errors.append("production readiness register next_authorised_item must be a valid PRD-0.x state, or PRD-1 after PRD-0.10 closure")
    boundaries = register.get("authority_boundaries", {})
    for key in TRUE_KEYS:
        if boundaries.get(key) is not True:
            errors.append(f"register boundary must preserve true runtime KG flag: {key}")
    for key in FALSE_KEYS:
        if boundaries.get(key) is not False:
            errors.append(f"register boundary must keep false: {key}")
    expected_files = [str(path) for path in CANONICAL_DOCS]
    if truth_map.get("canonical_files", []) != expected_files:
        errors.append("truth map must list the canonical current-state documentation files in order")
    corpus = "\n\n".join(read_text(p(path)) for path in CANONICAL_DOCS)
    for phrase in REQUIRED_PHRASES:
        if phrase not in corpus:
            errors.append(f"canonical docs must include required truth phrase: {phrase}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in corpus:
            errors.append(f"canonical docs must not contain stale phrase: {phrase}")
    if "Current-state refresh recorded: PRD-0.1" not in read_text(p(Path("docs/current_state.md"))):
        errors.append("docs/current_state.md must mark PRD-0.1 current-state refresh")
    if "PRD-0.2  Historical report and stale-source quarantine" not in read_text(p(Path("docs/roadmap/README.md"))):
        errors.append("roadmap README must show PRD-0.2 as the next PRD-0 cleanup item")
    captured = record.get("canonical_current_state_documentation_refresh_recorded") is True
    if captured:
        if record.get("prd_id") != PRD_ID:
            errors.append("captured PRD-0.1 record must identify PRD-0.1")
        for key in ["prd000_production_readiness_stream_authority_valid", "truth_map_recorded", "canonical_docs_refreshed", "stale_canonical_claims_removed"]:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.1 record flag must be true: {key}")
        for key in TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.1 record must preserve true runtime KG flag: {key}")
        for key in FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"captured PRD-0.1 record boundary must remain false: {key}")
    else:
        warnings.append("PRD-0.1 evidence has not been captured yet")
    authority_errors = [error for error in errors if not error.startswith("captured PRD-0.1 record")]
    authority_valid = not authority_errors
    final_valid = authority_valid and captured and not errors
    return {"authority_valid": authority_valid, "final_valid": final_valid, "recorded": captured, "prd_id": PRD_ID, "errors": errors, "warnings": warnings, "prd000_production_readiness_stream_authority_valid": prd000_valid, "truth_map_recorded": bool(truth_map), "canonical_docs_refreshed": not any("required truth phrase" in e for e in errors), "stale_canonical_claims_removed": not any("stale phrase" in e for e in errors), **{key: boundaries.get(key) for key in TRUE_KEYS + FALSE_KEYS}}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.1 authority valid: {result['authority_valid']}")
        print(f"PRD-0.1 final valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
