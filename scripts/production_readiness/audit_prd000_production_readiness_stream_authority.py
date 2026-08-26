#!/usr/bin/env python3
"""Audit PRD-0.0 production-readiness stream authority files and boundaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_final_roadmap_reconciliation_closure import evaluate as evaluate_rr_closure
from scripts.roadmap_reconciliation.verify_kg_roadmap_closure import evaluate as evaluate_kg_closure

PRD_ID = "PRD-0.0"
STREAM_ID = "PRD-PRODUCTION-READINESS"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
AUTHORITY_DOC = ROOT / "prd_000_production_readiness_stream_authority.md"
EXPANDED_PRD0 = ROOT / "prd_0_expanded_post_closure_current_state_authority_refresh.md"
BOUNDARY_CONTRACT = ROOT / "production_readiness_boundary_contract.md"
RECORD = ROOT / "prd_000_production_readiness_stream_authority_record.json"

PRD0_IDS = [f"PRD-0.{idx}" for idx in range(0, 11)]
PRD_IDS = [f"PRD-{idx}" for idx in range(1, 12)]
ALLOWED_NEXT_ITEMS = {f"PRD-0.{idx}" for idx in range(0, 11)} | {"PRD-1", "PRD-2"} | {f"PRD-1.{idx}" for idx in range(0, 10)} | {f"PRD-{idx}" for idx in range(1, 12)} | {f"PRD-11.0R.RUNTIME-RESTORE.EXECUTION-{idx}" for idx in range(1, 10)}
TRUE_KEYS = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "authority_switch_executed",
]
FALSE_KEYS = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "new_kg_slice_authorised",
    "prd1_implementation_authorised",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _ids(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row.get("prd_id")) for row in rows]


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    def p(path: Path) -> Path:
        return root / path

    register = read_json(p(REGISTER))
    record = read_json(p(RECORD))
    authority_text = read_text(p(AUTHORITY_DOC))
    prd0_text = read_text(p(EXPANDED_PRD0))
    boundary_text = read_text(p(BOUNDARY_CONTRACT))

    rr = evaluate_rr_closure(root)
    kg = evaluate_kg_closure(root)
    if rr.get("valid") is not True:
        errors.append("final RR roadmap reconciliation closure verifier must be valid")
    if kg.get("valid") is not True:
        errors.append("KG roadmap closure verifier must be valid")
    if kg.get("runtime_kg_implementation_claimed") is not True:
        errors.append("KG closure must preserve runtime KG implementation claimed true")
    if kg.get("runtime_kg_authority_switch_authorised") is not True:
        errors.append("KG closure must preserve runtime KG authority switch authorised true")
    if kg.get("authority_switch_executed") is not True:
        errors.append("KG closure must preserve authority switch executed true")

    for path in [REGISTER, AUTHORITY_DOC, EXPANDED_PRD0, BOUNDARY_CONTRACT, RECORD]:
        if not p(path).exists():
            errors.append(f"missing PRD-0.0 authority file: {path}")

    if register.get("stream_id") != STREAM_ID:
        errors.append("production readiness register must identify PRD-PRODUCTION-READINESS")
    if register.get("next_authorised_item") not in ALLOWED_NEXT_ITEMS:
        errors.append("production readiness register next_authorised_item must remain within PRD-0.0 through PRD-0.10, or PRD-1/PRD-2 after PRD-0.10 closure")

    prd0_ids = _ids(register.get("prd0_sequence", []))
    if prd0_ids != PRD0_IDS:
        errors.append("PRD-0 register sequence must contain PRD-0.0 through PRD-0.10 in order")
    prod_ids = _ids(register.get("production_readiness_sequence", []))
    if prod_ids != PRD_IDS:
        errors.append("production readiness sequence must contain PRD-1 through PRD-11 in order")

    gates = register.get("gates", {})
    for key in [
        "prd1_blocked_until_prd0_closure",
        "production_release_blocked_until_prd11",
        "public_beta_blocked_until_prd10",
        "billing_blocked_until_prd9",
        "new_kg_slice_blocked",
    ]:
        if gates.get(key) is not True:
            errors.append(f"production readiness gate must be true: {key}")

    boundaries = register.get("authority_boundaries", {})
    for key in TRUE_KEYS:
        if boundaries.get(key) is not True:
            errors.append(f"register boundary must preserve true runtime KG flag: {key}")
    for key in FALSE_KEYS:
        if boundaries.get(key) is not False:
            errors.append(f"register boundary must keep false: {key}")

    for required in [
        "PRD-0.1 — Canonical current-state documentation refresh",
        "PRD-0.10 — PRD-0 closure evidence and handoff to PRD-1",
        "Production release: not authorised",
        "New KG slice: not authorised",
    ]:
        if required not in authority_text:
            errors.append(f"authority doc must include: {required}")
    for required in ["PRD-0.0", "PRD-0.10", "PRD-11"]:
        if required not in prd0_text:
            errors.append(f"expanded PRD-0 doc must include {required}")
    for required in ["Production release", "Live learner traffic", "Additional KG slices"]:
        if required not in boundary_text:
            errors.append(f"boundary contract must include: {required}")

    captured = record.get("production_readiness_stream_authority_recorded") is True
    if captured:
        if record.get("prd_id") != PRD_ID:
            errors.append("captured PRD-0.0 record must identify PRD-0.0")
        if record.get("stream_id") != STREAM_ID:
            errors.append("captured PRD-0.0 record must identify PRD-PRODUCTION-READINESS")
        for key in [
            "rr_closure_valid",
            "kg_closure_valid",
            "prd0_sequence_registered",
            "prd1_blocked_until_prd0_closure",
            "known_caveats_carried_forward",
        ]:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.0 record flag must be true: {key}")
        for key in TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.0 record must preserve true runtime KG flag: {key}")
        for key in FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"captured PRD-0.0 record boundary must remain false: {key}")
    else:
        warnings.append("PRD-0.0 evidence has not been captured yet")

    authority_errors = [
        error for error in errors
        if not error.startswith("captured PRD-0.0 record")
    ]
    authority_valid = not authority_errors
    final_valid = authority_valid and captured and not errors
    return {
        "authority_valid": authority_valid,
        "final_valid": final_valid,
        "recorded": captured,
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "errors": errors,
        "warnings": warnings,
        "rr_closure_valid": rr.get("valid") is True,
        "kg_closure_valid": kg.get("valid") is True,
        "prd0_sequence_registered": prd0_ids == PRD0_IDS,
        "production_readiness_sequence_registered": prod_ids == PRD_IDS,
        "prd1_blocked_until_prd0_closure": gates.get("prd1_blocked_until_prd0_closure") is True,
        "runtime_kg_implementation_claimed": boundaries.get("runtime_kg_implementation_claimed"),
        "runtime_kg_authority_switch_authorised": boundaries.get("runtime_kg_authority_switch_authorised"),
        "authority_switch_executed": boundaries.get("authority_switch_executed"),
        "production_release_authorised": boundaries.get("production_release_authorised"),
        "deployment_authorised": boundaries.get("deployment_authorised"),
        "release_tag_authorised": boundaries.get("release_tag_authorised"),
        "public_beta_authorised": boundaries.get("public_beta_authorised"),
        "public_beta_live_traffic_authorised": boundaries.get("public_beta_live_traffic_authorised"),
        "live_learner_traffic_authorised": boundaries.get("live_learner_traffic_authorised"),
        "billing_launch_authorised": boundaries.get("billing_launch_authorised"),
        "live_payment_processing_authorised": boundaries.get("live_payment_processing_authorised"),
        "new_kg_slice_authorised": boundaries.get("new_kg_slice_authorised"),
        "prd1_implementation_authorised": boundaries.get("prd1_implementation_authorised"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.0 authority valid: {result['authority_valid']}")
        print(f"PRD-0.0 final valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
