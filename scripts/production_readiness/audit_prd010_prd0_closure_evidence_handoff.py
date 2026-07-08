#!/usr/bin/env python3
"""Audit PRD-0.10 PRD-0 closure evidence and PRD-1 handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from scripts.roadmap_reconciliation.verify_prd000_production_readiness_stream_authority import evaluate as evaluate_prd000
from scripts.roadmap_reconciliation.verify_prd001_canonical_current_state_documentation_refresh import evaluate as evaluate_prd001
from scripts.roadmap_reconciliation.verify_prd002_historical_report_stale_source_quarantine import evaluate as evaluate_prd002
from scripts.roadmap_reconciliation.verify_prd003_documentation_housekeeping_ratchet_refresh import evaluate as evaluate_prd003
from scripts.roadmap_reconciliation.verify_prd004_test_dependency_bootstrap_baseline import evaluate as evaluate_prd004
from scripts.roadmap_reconciliation.verify_prd005_test_failure_collection_stabilisation_register import evaluate as evaluate_prd005
from scripts.roadmap_reconciliation.verify_prd006_workflow_command_hygiene_ci_inventory import evaluate as evaluate_prd006
from scripts.roadmap_reconciliation.verify_prd007_openapi_generated_artifact_canonicalisation import evaluate as evaluate_prd007
from scripts.roadmap_reconciliation.verify_prd008_branch_release_naming_reconciliation import evaluate as evaluate_prd008
from scripts.roadmap_reconciliation.verify_prd009_repository_hygiene_generated_local_artifact_audit import evaluate as evaluate_prd009

PRD_ID = "PRD-0.10"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_010_prd0_closure_evidence_handoff.md"
PLAN = ROOT / "prd0_closure_evidence_handoff_plan.md"
SCHEMA_DOC = ROOT / "prd0_closure_evidence_handoff.schema.md"
CHECKLIST = ROOT / "prd0_closure_handoff_checklist.md"
RECORD = ROOT / "prd_010_prd0_closure_evidence_handoff_record.json"
SNAPSHOT = ROOT / "prd0_closure_evidence_handoff.json"
HANDOFF_DOC = Path("docs/engineering/prd0_to_prd1_handoff.md")

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
    "prd1_implementation_authorised",
]
VERIFY_CHAIN: list[tuple[str, Callable[[Path], dict[str, Any]]]] = [
    ("PRD-0.0", evaluate_prd000),
    ("PRD-0.1", evaluate_prd001),
    ("PRD-0.2", evaluate_prd002),
    ("PRD-0.3", evaluate_prd003),
    ("PRD-0.4", evaluate_prd004),
    ("PRD-0.5", evaluate_prd005),
    ("PRD-0.6", evaluate_prd006),
    ("PRD-0.7", evaluate_prd007),
    ("PRD-0.8", evaluate_prd008),
    ("PRD-0.9", evaluate_prd009),
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def prd0_verifier_results(root: Path) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for prd_id, fn in VERIFY_CHAIN:
        try:
            result = fn(root)
        except Exception as exc:  # pragma: no cover - defensive report path
            result = {"valid": False, "authority_valid": False, "errors": [repr(exc)]}
        results[prd_id] = {
            "valid": result.get("valid") is True,
            "authority_valid": result.get("authority_valid") is True,
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
        }
    return results


def all_predecessors_valid(results: dict[str, dict[str, Any]]) -> bool:
    return bool(results) and all(item.get("valid") is True for item in results.values())


def prd1_subslice_started(register: dict[str, Any]) -> bool:
    last_item = str(register.get("last_recorded_item", ""))
    next_item = str(register.get("next_authorised_item", ""))
    return last_item.startswith("PRD-1.") and next_item.startswith("PRD-1.")


def prd0_sequence_complete(register: dict[str, Any]) -> bool:
    sequence = register.get("prd0_sequence", [])
    expected = [f"PRD-0.{idx}" for idx in range(0, 11)]
    ids = [str(item.get("prd_id")) for item in sequence]
    if ids != expected:
        return False
    return all(item.get("authorised") is True and item.get("status") == "recorded" for item in sequence)


def prd1_handoff_ready(register: dict[str, Any]) -> bool:
    if register.get("next_authorised_item") != "PRD-1" and not prd1_subslice_started(register):
        return False
    for item in register.get("production_readiness_sequence", []):
        if item.get("prd_id") == "PRD-1":
            return item.get("authorised") is True and item.get("status") in {"authorised", "next_authorised", "in_progress", "recorded"}
    return False


def closure_snapshot(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    register = read_json(root / REGISTER)
    results = prd0_verifier_results(root)
    return {
        "schema_version": "prd0-closure-evidence-handoff/v1",
        "prd_id": PRD_ID,
        "captured_at": captured_at,
        "prd0_verifier_results": results,
        "all_prd0_predecessors_valid": all_predecessors_valid(results),
        "register_summary": {
            "last_recorded_item": register.get("last_recorded_item"),
            "next_authorised_item": register.get("next_authorised_item"),
            "prd0_sequence_complete": prd0_sequence_complete(register),
            "prd1_handoff_ready": prd1_handoff_ready(register),
        },
        "authority_boundaries": {
            **{key: True for key in TRUE_KEYS},
            **{key: False for key in FALSE_KEYS},
        },
        "handoff": {
            "prd0_closed": register.get("last_recorded_item") == PRD_ID or prd1_subslice_started(register),
            "next_authorised_item": register.get("next_authorised_item"),
            "prd1_handoff_authorised": prd1_handoff_ready(register),
            "no_prd1_implementation_performed": True,
        },
    }


def audit(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    register = read_json(root / REGISTER)
    record = read_json(root / RECORD)
    saved_snapshot = read_json(root / SNAPSHOT)
    live_snapshot = closure_snapshot(root)
    results = live_snapshot["prd0_verifier_results"]

    for path in [PRD_DOC, PLAN, SCHEMA_DOC, CHECKLIST, RECORD, HANDOFF_DOC]:
        if not (root / path).exists():
            errors.append(f"missing required PRD-0.10 file: {path}")

    if register.get("last_recorded_item") not in {"PRD-0.9", "PRD-0.10"} | {f"PRD-1.{idx}" for idx in range(0, 10)}:
        errors.append("production readiness register must be positioned at PRD-0.9 or terminal PRD-0.10")
    if register.get("last_recorded_item") == "PRD-0.9" and register.get("next_authorised_item") != PRD_ID:
        errors.append("production readiness register must authorise PRD-0.10 after PRD-0.9")
    if register.get("last_recorded_item") == PRD_ID and register.get("next_authorised_item") != "PRD-1":
        errors.append("terminal PRD-0.10 register state must authorise PRD-1 next")
    if prd1_subslice_started(register) and not prd1_handoff_ready(register):
        errors.append("advanced PRD-1 register state must preserve PRD-1 handoff readiness")

    for prd_id, result in results.items():
        if result.get("valid") is not True:
            errors.append(f"{prd_id} verifier must be valid before PRD-0.10 closure")

    prd_doc = read_text(root / PRD_DOC)
    plan = read_text(root / PLAN)
    schema = read_text(root / SCHEMA_DOC)
    checklist = read_text(root / CHECKLIST)
    handoff = read_text(root / HANDOFF_DOC)
    required_text = [
        (prd_doc, "PRD-1 — Required CI and Release Gate Convergence", "PRD-0.10 doc must identify PRD-1 handoff"),
        (prd_doc, "does not implement PRD-1", "PRD-0.10 doc must preserve no-implementation boundary"),
        (plan, "last_recorded_item", "PRD-0.10 plan must describe terminal register state"),
        (schema, "prd0-closure-evidence-handoff/v1", "PRD-0.10 schema must define snapshot version"),
        (checklist, "PRD-0.9 verifier valid", "PRD-0.10 checklist must include PRD-0.9"),
        (handoff, "This handoff does not itself implement PRD-1", "handoff document must preserve no-implementation boundary"),
    ]
    for text, phrase, message in required_text:
        if phrase not in text:
            errors.append(message)

    for key in TRUE_KEYS:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
    for key in FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")

    if record.get("prd009_repository_hygiene_generated_local_artifact_audit_valid") is not True:
        errors.append("PRD-0.9 validity must be recorded")
    if record.get("all_prd0_predecessors_valid") is not True:
        errors.append("all PRD-0 predecessor validity must be recorded")
    if record.get("prd0_closure_checklist_refreshed") is not True:
        errors.append("PRD-0 closure checklist must be refreshed")
    if record.get("prd1_handoff_document_refreshed") is not True:
        errors.append("PRD-1 handoff document must be refreshed")
    if record.get("no_prd1_implementation_performed") is not True:
        errors.append("no_prd1_implementation_performed must be true")

    authority_valid = not errors
    recorded = record.get("prd0_closure_evidence_recorded") is True
    handoff_recorded = record.get("prd0_handoff_to_prd1_recorded") is True
    snapshot_recorded = (
        saved_snapshot.get("schema_version") == "prd0-closure-evidence-handoff/v1"
        and saved_snapshot.get("prd_id") == PRD_ID
        and saved_snapshot.get("all_prd0_predecessors_valid") is True
    )
    final_valid = (
        authority_valid
        and recorded
        and handoff_recorded
        and snapshot_recorded
        and record.get("prd0_sequence_complete") is True
        and record.get("prd1_handoff_authorised") is True
        and record.get("next_authorised_item") == "PRD-1"
        and (
            (register.get("last_recorded_item") == PRD_ID and register.get("next_authorised_item") == "PRD-1")
            or prd1_subslice_started(register)
        )
        and prd0_sequence_complete(register)
        and prd1_handoff_ready(register)
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-0.10 authority is valid but closure evidence capture has not completed")

    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "errors": errors,
        "warnings": warnings,
        "prd009_repository_hygiene_generated_local_artifact_audit_valid": results.get("PRD-0.9", {}).get("valid") is True,
        "all_prd0_predecessors_valid": all_predecessors_valid(results),
        "prd0_closure_evidence_recorded": recorded,
        "prd0_handoff_to_prd1_recorded": handoff_recorded,
        "prd0_sequence_complete": prd0_sequence_complete(register),
        "prd1_handoff_authorised": record.get("prd1_handoff_authorised") is True,
        "prd1_handoff_ready": prd1_handoff_ready(register),
        "snapshot_recorded": snapshot_recorded,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "no_prd1_implementation_performed": record.get("no_prd1_implementation_performed") is True,
        **{key: record.get(key) is True for key in TRUE_KEYS},
        **{key: record.get(key) is True for key in FALSE_KEYS},
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
        print(f"PRD-0.10 valid: {result['valid']}")
        print(f"PRD-0.10 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
