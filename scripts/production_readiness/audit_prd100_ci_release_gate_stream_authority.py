
#!/usr/bin/env python3
"""Audit PRD-1.0 CI/release-gate stream authority and register."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd010_prd0_closure_evidence_handoff import evaluate as evaluate_prd010

PRD_ID = "PRD-1.0"
STREAM_ID = "PRD-1-CI-RELEASE-GATE-CONVERGENCE"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD1_REGISTER = ROOT / "prd1_ci_release_gate_register.json"
PRD_DOC = ROOT / "prd_100_ci_release_gate_stream_authority.md"
PLAN = ROOT / "prd1_ci_release_gate_stream_authority_plan.md"
SCHEMA_DOC = ROOT / "prd1_ci_release_gate_register.schema.md"
SEQUENCE_DOC = ROOT / "prd1_ci_release_gate_sequence.md"
RECORD = ROOT / "prd_100_ci_release_gate_stream_authority_record.json"
SNAPSHOT = ROOT / "prd1_ci_release_gate_stream_authority.json"
ENGINEERING_DOC = Path("docs/engineering/prd1_ci_release_gate_convergence.md")

TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
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
    "prd2_implementation_authorised",
]
NO_CHANGE_KEYS = [
    "ci_workflow_changes_performed",
    "required_checks_enforced",
    "release_gate_enforced",
    "branch_protection_modified",
    "workflow_canonicalisation_performed",
    "openapi_reconciliation_performed",
]
EXPECTED_SEQUENCE = [f"PRD-1.{idx}" for idx in range(10)]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def prd1_sequence_registered(prd1_register: dict[str, Any]) -> bool:
    sequence = prd1_register.get("prd1_sequence", [])
    ids = [str(item.get("prd_id")) for item in sequence]
    return ids == EXPECTED_SEQUENCE


def prd1_0_recorded(prd1_register: dict[str, Any]) -> bool:
    last_item = str(prd1_register.get("last_recorded_item", ""))
    next_item = str(prd1_register.get("next_authorised_item", ""))
    if last_item == PRD_ID and next_item == "PRD-1.1":
        positioned = True
    elif last_item.startswith("PRD-1.") and last_item != PRD_ID and (next_item.startswith("PRD-1.") or next_item in {"PRD-2", "PRD-3"}):
        positioned = True
    else:
        positioned = False
    if not positioned:
        return False
    for item in prd1_register.get("prd1_sequence", []):
        if item.get("prd_id") == PRD_ID and not (item.get("authorised") is True and item.get("status") == "recorded"):
            return False
        if item.get("prd_id") == "PRD-1.1" and not (item.get("authorised") is True and item.get("status") in {"authorised", "next_authorised", "recorded"}):
            return False
    return True


def production_register_position(register: dict[str, Any]) -> str:
    last_item = str(register.get("last_recorded_item", ""))
    next_item = str(register.get("next_authorised_item", ""))
    if last_item == "PRD-0.10" and next_item == "PRD-1":
        return "after_prd0_handoff_before_prd1_capture"
    if last_item == PRD_ID and next_item == "PRD-1.1":
        return "prd1_0_recorded"
    if last_item.startswith("PRD-1.") and last_item != PRD_ID and next_item.startswith("PRD-1."):
        return "advanced_prd1_subslice"
    if last_item == "PRD-1.9" and next_item in {"PRD-2", "PRD-3"}:
        return "prd1_closed_prd2_authorised"
    if next_item.startswith("PRD-11.0R.RUNTIME-RESTORE") or last_item.startswith("PRD-11.0R.RUNTIME-RESTORE") or last_item in {f"PRD-{idx}" for idx in range(1, 12)}:
        return "advanced_authorized_execution"
    return "unexpected"


def authority_snapshot(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    register = read_json(root / REGISTER)
    prd1_register = read_json(root / PRD1_REGISTER)
    return {
        "schema_version": "prd1-ci-release-gate-stream-authority/v1",
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "captured_at": captured_at,
        "production_readiness_register_summary": {
            "last_recorded_item": register.get("last_recorded_item"),
            "next_authorised_item": register.get("next_authorised_item"),
            "position": production_register_position(register),
        },
        "prd1_register_summary": {
            "last_recorded_item": prd1_register.get("last_recorded_item"),
            "next_authorised_item": prd1_register.get("next_authorised_item"),
            "prd1_sequence_registered": prd1_sequence_registered(prd1_register),
            "prd1_0_recorded": prd1_0_recorded(prd1_register),
        },
        "authority_boundaries": {**{key: True for key in TRUE_KEYS}, **{key: False for key in FALSE_KEYS}},
        "implementation_boundaries": {key: False for key in NO_CHANGE_KEYS},
        "next_authorised_item": "PRD-1.1" if prd1_0_recorded(prd1_register) else PRD_ID,
    }


def audit(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    register = read_json(root / REGISTER)
    prd1_register = read_json(root / PRD1_REGISTER)
    record = read_json(root / RECORD)
    snapshot = read_json(root / SNAPSHOT)
    prd010 = evaluate_prd010(root)

    for path in [PRD_DOC, PLAN, SCHEMA_DOC, SEQUENCE_DOC, RECORD, PRD1_REGISTER, ENGINEERING_DOC]:
        if not (root / path).exists():
            errors.append(f"missing required PRD-1.0 file: {path}")

    if not (prd010.get("valid") is True or prd010.get("authority_valid") is True):
        errors.append("PRD-0.10 verifier must remain valid before PRD-1.0")
    if production_register_position(register) == "unexpected":
        errors.append("production readiness register must be positioned at PRD-0.10/PRD-1, PRD-1.0/PRD-1.1, or a later PRD-1.x slice")
    if prd1_register.get("schema_version") != "prd1-ci-release-gate-register/v1":
        errors.append("PRD-1 register schema_version must be prd1-ci-release-gate-register/v1")
    if prd1_register.get("stream_id") != STREAM_ID:
        errors.append("PRD-1 register stream_id must be canonical")
    if prd1_register.get("parent_stream_id") != "PRD-PRODUCTION-READINESS":
        errors.append("PRD-1 register parent stream must be PRD-PRODUCTION-READINESS")
    if prd1_register.get("authorised_by_prd0_10") is not True:
        errors.append("PRD-1 register must be authorised by PRD-0.10 handoff")
    if not prd1_sequence_registered(prd1_register):
        errors.append("PRD-1 register must contain PRD-1.0 through PRD-1.9 sequence")

    required_text = [
        (read_text(root / PRD_DOC), "PRD-1.1 — CI inventory authority", "PRD-1.0 doc must identify PRD-1.1 as the next slice"),
        (read_text(root / PRD_DOC), "does not modify CI workflows", "PRD-1.0 doc must preserve no-CI-change boundary"),
        (read_text(root / PLAN), "last_recorded_item", "PRD-1.0 plan must describe terminal register state"),
        (read_text(root / SCHEMA_DOC), "prd1-ci-release-gate-register/v1", "PRD-1 schema must define register version"),
        (read_text(root / SEQUENCE_DOC), "PRD-1.9", "PRD-1 sequence document must include PRD-1.9 handoff"),
        (read_text(root / ENGINEERING_DOC), "Runtime KG implementation is reserved for PRD-2", "engineering doc must preserve PRD-2 boundary"),
    ]
    for text, phrase, message in required_text:
        if phrase not in text:
            errors.append(message)

    for key in TRUE_KEYS:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
        if prd1_register.get("authority_boundaries", {}).get(key) is not True:
            errors.append(f"PRD-1 register {key} must remain true")
    for key in FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
        if prd1_register.get("authority_boundaries", {}).get(key) is not False:
            errors.append(f"PRD-1 register {key} must remain false")
    for key in NO_CHANGE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false in PRD-1.0")
        if production_register_position(register) == "prd1_0_recorded" and prd1_register.get("implementation_boundaries", {}).get(key) is not False:
            errors.append(f"PRD-1 register {key} must remain false")

    for key in [
        "no_ci_workflow_changes_performed",
        "no_required_check_enforcement_performed",
        "no_release_gate_enforcement_performed",
        "no_branch_protection_change_performed",
        "no_openapi_reconciliation_performed",
        "no_prd2_implementation_performed",
    ]:
        if record.get(key) is not True:
            errors.append(f"{key} must be true")

    authority_valid = not errors
    recorded = record.get("prd1_stream_authority_recorded") is True and record.get("prd1_authority_evidence_recorded") is True
    snapshot_recorded = (
        snapshot.get("schema_version") == "prd1-ci-release-gate-stream-authority/v1"
        and snapshot.get("prd_id") == PRD_ID
        and snapshot.get("prd1_register_summary", {}).get("prd1_sequence_registered") is True
    )
    final_valid = (
        authority_valid
        and recorded
        and snapshot_recorded
        and prd1_0_recorded(prd1_register)
        and production_register_position(register) in {"prd1_0_recorded", "advanced_prd1_subslice", "prd1_closed_prd2_authorised"}
        and record.get("next_authorised_item") == "PRD-1.1"
        and record.get("prd1_1_authorised") is True
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-1.0 authority is valid but evidence capture has not completed")

    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "errors": errors,
        "warnings": warnings,
        "prd010_prd0_closure_evidence_handoff_valid": prd010.get("valid") is True,
        "prd1_register_created": bool(prd1_register),
        "prd1_sequence_registered": prd1_sequence_registered(prd1_register),
        "prd1_stream_authority_recorded": recorded,
        "prd1_authority_evidence_recorded": record.get("prd1_authority_evidence_recorded") is True,
        "prd1_0_recorded": prd1_0_recorded(prd1_register),
        "prd1_1_authorised": record.get("prd1_1_authorised") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_position": production_register_position(register),
        "snapshot_recorded": snapshot_recorded,
        "no_ci_workflow_changes_performed": record.get("no_ci_workflow_changes_performed") is True,
        "no_required_check_enforcement_performed": record.get("no_required_check_enforcement_performed") is True,
        "no_release_gate_enforcement_performed": record.get("no_release_gate_enforcement_performed") is True,
        "no_branch_protection_change_performed": record.get("no_branch_protection_change_performed") is True,
        "no_openapi_reconciliation_performed": record.get("no_openapi_reconciliation_performed") is True,
        "no_prd2_implementation_performed": record.get("no_prd2_implementation_performed") is True,
        **{key: record.get(key) is True for key in TRUE_KEYS},
        **{key: record.get(key) is True for key in FALSE_KEYS},
        **{key: record.get(key) is True for key in NO_CHANGE_KEYS},
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
        print(f"PRD-1.0 valid: {result['valid']}")
        print(f"PRD-1.0 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
