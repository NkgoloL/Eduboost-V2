#!/usr/bin/env python3
"""Audit PRD-1.5-1.9 CI convergence, release readiness, final evidence, and PRD-2 handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.production_readiness.apply_prd105_109_ci_convergence_release_readiness_handoff import (
    CONFIG,
    DOC,
    ENGINEERING_DOC,
    FALSE_BOUNDARIES,
    IMPLEMENTATION_FALSE,
    MERGED_PRD_SLICES,
    PRD_ID,
    RECORD,
    STREAM_ID,
    TRUE_BOUNDARIES,
    build_config,
)
from scripts.roadmap_reconciliation.verify_prd100_ci_release_gate_stream_authority import evaluate as evaluate_prd100
from scripts.roadmap_reconciliation.verify_prd101_ci_inventory_authority import evaluate as evaluate_prd101
from scripts.roadmap_reconciliation.verify_prd102_104_required_checks_workflow_release_gate_convergence import evaluate as evaluate_prd102_104

ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD1_REGISTER = ROOT / "prd1_ci_release_gate_register.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def prd1_register_position(prd1_register: dict[str, Any]) -> str:
    last_item = prd1_register.get("last_recorded_item")
    next_item = prd1_register.get("next_authorised_item")
    if (last_item, next_item) == ("PRD-1.4", "PRD-1.5"):
        return "after_prd1_4_before_final_capture"
    if last_item == "PRD-1.9" and next_item in {"PRD-2", "PRD-3"}:
        return "prd1_closed_prd2_authorised"
    return "unexpected"


def production_register_position(register: dict[str, Any]) -> str:
    last_item = register.get("last_recorded_item")
    next_item = register.get("next_authorised_item")
    if (last_item, next_item) == ("PRD-1.4", "PRD-1.5"):
        return "after_prd1_4_before_final_capture"
    if last_item == "PRD-1.9" and next_item in {"PRD-2", "PRD-3"}:
        return "prd1_closed_prd2_authorised"
    if str(last_item).startswith("PRD-2.") and next_item == "PRD-3":
        return "prd1_closed_prd2_authorised"
    return "unexpected"

def prd1_sequence_complete(prd1_register: dict[str, Any]) -> bool:
    expected = [f"PRD-1.{idx}" for idx in range(10)]
    sequence = prd1_register.get("prd1_sequence", [])
    ids = [str(item.get("prd_id")) for item in sequence]
    if ids != expected:
        return False
    return all(item.get("authorised") is True and item.get("status") == "recorded" for item in sequence)


def prd2_authorised_in_production_sequence(register: dict[str, Any]) -> bool:
    for item in register.get("production_readiness_sequence", []):
        if item.get("prd_id") == "PRD-2":
            return item.get("authorised") is True and item.get("status") in {"authorised", "next_authorised", "in_progress"}
    return False


def audit(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    register = read_json(root / REGISTER)
    prd1_register = read_json(root / PRD1_REGISTER)
    record = read_json(root / RECORD)
    config = read_json(root / CONFIG)
    live_config = build_config(root)

    prd100 = evaluate_prd100(root)
    prd101 = evaluate_prd101(root)
    prd102_104 = evaluate_prd102_104(root)

    for path in [DOC, ENGINEERING_DOC, CONFIG, RECORD]:
        if not (root / path).exists():
            errors.append(f"missing required PRD-1.5-1.9 file: {path}")

    if prd100.get("valid") is not True:
        errors.append("PRD-1.0 verifier must remain valid")
    if prd101.get("valid") is not True:
        errors.append("PRD-1.1 verifier must remain valid")
    if prd102_104.get("valid") is not True:
        errors.append("PRD-1.2-1.4 verifier must remain valid")
    if prd1_register_position(prd1_register) == "unexpected":
        errors.append("PRD-1 register must be positioned at PRD-1.4/PRD-1.5 or PRD-1.9/PRD-2")
    if production_register_position(register) == "unexpected":
        errors.append("production readiness register must be positioned at PRD-1.4/PRD-1.5 or PRD-1.9/PRD-2")

    if config.get("schema_version") != "prd1-ci-convergence-release-readiness-handoff/v1":
        errors.append("PRD-1.5-1.9 config schema_version must be canonical")
    if config.get("merged_prd_slices") != MERGED_PRD_SLICES:
        errors.append("config must declare merged PRD-1.5 through PRD-1.9 scope")
    if config.get("ci_convergence_evidence", {}).get("python_m_pytest_workflow_count") != 0:
        errors.append("config must show no remaining workflow-level python -m pytest calls")
    if live_config.get("workflow_summary", {}).get("python_m_pytest_workflow_count") != 0:
        errors.append("live workflow scan still finds python -m pytest")
    if config.get("ci_convergence_evidence", {}).get("openapi_root_and_docs_match") is not True:
        errors.append("config must show root and docs OpenAPI artifacts still match")
    if live_config.get("openapi_summary", {}).get("root_and_docs_openapi_match") is not True:
        errors.append("live root and docs OpenAPI artifacts do not match")
    coverage = config.get("ci_convergence_evidence", {}).get("required_signal_coverage", {})
    for key in ["python-package-and-unit-tests", "openapi-contract-and-drift", "security-and-dependency-scan", "migration-and-runtime-contracts"]:
        if coverage.get(key) is not True:
            errors.append(f"required signal coverage missing for {key}")

    combined_text = read_text(root / DOC) + read_text(root / ENGINEERING_DOC)
    for phrase, message in [
        ("Merged slices", "PRD doc must state merged slices"),
        ("PRD-2 — Runtime KG Integration and Persistence", "PRD doc must identify PRD-2 handoff"),
        ("does **not** modify branch protection", "PRD doc must preserve branch-protection boundary"),
        ("PRD-11 remains the production release/deployment authority", "docs must preserve PRD-11 boundary"),
        ("Runtime KG implementation remains reserved for PRD-2", "engineering doc must preserve PRD-2 boundary"),
    ]:
        if phrase not in combined_text:
            errors.append(message)

    for key in TRUE_BOUNDARIES:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
    for key in FALSE_BOUNDARIES:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
    for key in IMPLEMENTATION_FALSE:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")

    for key in [
        "required_checks_enforced",
        "release_gate_enforced",
        "branch_protection_modified",
        "prd2_implementation_authorised",
        "production_release_authorised",
        "deployment_authorised",
        "release_tag_authorised",
    ]:
        if record.get(key) is not False:
            errors.append(f"{key} must be false")

    authority_valid = not errors
    evidence_recorded = record.get("ci_convergence_evidence_recorded") is True
    release_readiness_recorded = record.get("release_readiness_register_recorded") is True
    reconciliation_recorded = record.get("prd1_final_reconciliation_recorded") is True
    final_evidence_recorded = record.get("prd1_final_evidence_recorded") is True
    handoff_recorded = record.get("prd2_handoff_authorised") is True
    final_valid = (
        authority_valid
        and evidence_recorded
        and release_readiness_recorded
        and reconciliation_recorded
        and final_evidence_recorded
        and handoff_recorded
        and prd1_sequence_complete(prd1_register)
        and prd2_authorised_in_production_sequence(register)
        and production_register_position(register) == "prd1_closed_prd2_authorised"
        and prd1_register_position(prd1_register) == "prd1_closed_prd2_authorised"
        and record.get("next_authorised_item") == "PRD-2"
        and register.get("next_authorised_item") in {"PRD-2", "PRD-3"}
        and prd1_register.get("next_authorised_item") == "PRD-2"
        and record.get("prd2_implementation_authorised") is False
        and record.get("no_prd2_implementation_performed") is True
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-1.5-1.9 authority is valid but final evidence capture has not completed")

    workflow_summary = live_config.get("workflow_summary", {})
    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": MERGED_PRD_SLICES,
        "stream_id": STREAM_ID,
        "errors": errors,
        "warnings": warnings,
        "prd100_ci_release_gate_stream_authority_valid": prd100.get("valid") is True,
        "prd101_ci_inventory_authority_valid": prd101.get("valid") is True,
        "prd102_104_required_checks_workflow_release_gate_valid": prd102_104.get("valid") is True,
        "ci_convergence_evidence_recorded": evidence_recorded,
        "release_readiness_register_recorded": release_readiness_recorded,
        "prd1_final_reconciliation_recorded": reconciliation_recorded,
        "prd1_final_evidence_recorded": final_evidence_recorded,
        "prd1_sequence_complete": prd1_sequence_complete(prd1_register),
        "prd2_handoff_authorised": handoff_recorded,
        "prd2_authorised_in_production_sequence": prd2_authorised_in_production_sequence(register),
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "prd1_register_next_authorised_item": prd1_register.get("next_authorised_item"),
        "production_register_position": production_register_position(register),
        "prd1_register_position": prd1_register_position(prd1_register),
        "python_m_pytest_workflow_count": workflow_summary.get("python_m_pytest_workflow_count"),
        "python3_m_pytest_workflow_count": workflow_summary.get("python3_m_pytest_workflow_count"),
        "openapi_root_and_docs_match": live_config.get("openapi_summary", {}).get("root_and_docs_openapi_match") is True,
        "required_checks_enforced": record.get("required_checks_enforced") is True,
        "release_gate_enforced": record.get("release_gate_enforced") is True,
        "branch_protection_modified": record.get("branch_protection_modified") is True,
        "prd2_implementation_authorised": record.get("prd2_implementation_authorised") is True,
        **{key: record.get(key) is True for key in TRUE_BOUNDARIES},
        **{key: record.get(key) is True for key in FALSE_BOUNDARIES},
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
        print(f"PRD-1.5-1.9 valid: {result['valid']}")
        print(f"PRD-1.5-1.9 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
