#!/usr/bin/env python3
"""Audit PRD-1.2-1.4 required-check, workflow, and release-gate convergence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.production_readiness.apply_prd102_104_required_checks_workflow_release_gate_convergence import (
    CONFIG,
    DOC,
    ENGINEERING_DOC,
    FALSE_BOUNDARIES,
    PRD_ID,
    RECORD,
    REQUIRED_CHECKS,
    STREAM_ID,
    TRUE_BOUNDARIES,
    build_config,
)
from scripts.roadmap_reconciliation.verify_prd101_ci_inventory_authority import evaluate as evaluate_prd101

ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD1_REGISTER = ROOT / "prd1_ci_release_gate_register.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def prd1_register_position(prd1_register: dict[str, Any]) -> str:
    pair = (prd1_register.get("last_recorded_item"), prd1_register.get("next_authorised_item"))
    if pair == ("PRD-1.1", "PRD-1.2"):
        return "after_prd1_1_before_convergence_capture"
    if pair == ("PRD-1.4", "PRD-1.5"):
        return "prd1_2_1_4_recorded_prd1_5_authorised"
    if pair == ("PRD-1.9", "PRD-2"):
        return "prd1_closed_after_prd1_4"
    return "unexpected"


def sequence_items_recorded(prd1_register: dict[str, Any]) -> bool:
    statuses = {item.get("prd_id"): item for item in prd1_register.get("prd1_sequence", [])}
    return all(
        statuses.get(prd_id, {}).get("status") == "recorded"
        and statuses.get(prd_id, {}).get("authorised") is True
        for prd_id in ["PRD-1.2", "PRD-1.3", "PRD-1.4"]
    )


def prd1_5_authorised(prd1_register: dict[str, Any]) -> bool:
    for item in prd1_register.get("prd1_sequence", []):
        if item.get("prd_id") == "PRD-1.5":
            return item.get("authorised") is True and item.get("status") in {"authorised", "next_authorised", "recorded"}
    return False


def audit(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    register = read_json(root / REGISTER)
    prd1_register = read_json(root / PRD1_REGISTER)
    record = read_json(root / RECORD)
    config = read_json(root / CONFIG)
    live_config = build_config(root, [])
    prd101 = evaluate_prd101(root)

    for path in [DOC, ENGINEERING_DOC, CONFIG, RECORD]:
        if not (root / path).exists():
            errors.append(f"missing required PRD-1.2-1.4 file: {path}")

    if prd101.get("valid") is not True:
        errors.append("PRD-1.1 verifier must remain valid before PRD-1.2-1.4")
    if prd1_register.get("schema_version") != "prd1-ci-release-gate-register/v1":
        errors.append("PRD-1 register schema_version must remain canonical")
    if prd1_register.get("stream_id") != STREAM_ID:
        errors.append("PRD-1 register stream_id must remain canonical")
    if prd1_register_position(prd1_register) == "unexpected":
        errors.append("PRD-1 register must be positioned at PRD-1.1/PRD-1.2 or PRD-1.4/PRD-1.5")

    if config.get("schema_version") != "prd1-required-checks-workflow-release-gate-convergence/v1":
        errors.append("required-check/workflow/release-gate config must use canonical schema")
    if config.get("merged_prd_slices") != ["PRD-1.2", "PRD-1.3", "PRD-1.4"]:
        errors.append("config must declare merged PRD-1.2, PRD-1.3, and PRD-1.4 scope")
    if len(config.get("required_check_classification", {}).get("required_checks", [])) < len(REQUIRED_CHECKS):
        errors.append("required-check classification must include the baseline required checks")
    if config.get("workflow_canonicalisation", {}).get("workflow_summary_after_canonicalisation", {}).get("python_m_pytest_workflow_count") != 0:
        errors.append("repository workflow pytest calls must be canonicalised to python3 -m pytest")
    if live_config.get("workflow_canonicalisation", {}).get("workflow_summary_after_canonicalisation", {}).get("python_m_pytest_workflow_count") != 0:
        errors.append("live workflow scan still finds python -m pytest")
    if config.get("openapi_reconciliation", {}).get("root_and_docs_openapi_match") is not True:
        errors.append("docs/openapi.json and root openapi.json must match")
    if config.get("release_gate_definition", {}).get("canonical_trunk_branch") != "master":
        errors.append("release gate definition must preserve master as canonical trunk")
    if config.get("release_gate_definition", {}).get("branch_protection_modified") is not False:
        errors.append("PRD-1.2-1.4 must not claim branch protection was modified")
    if config.get("release_gate_definition", {}).get("release_gate_enforced") is not False:
        errors.append("PRD-1.2-1.4 must define but not enforce the release gate")

    combined_text = read_text(root / DOC) + read_text(root / ENGINEERING_DOC)
    for phrase, message in [
        ("Merged slices", "PRD doc must state merged slices"),
        ("PRD-1.5", "PRD doc must identify PRD-1.5 as next slice"),
        ("does **not** enforce GitHub branch protection", "PRD doc must preserve branch-protection boundary"),
        ("PRD-11 remains the production release/deployment authority", "engineering doc must preserve PRD-11 boundary"),
        ("PRD-2 remains the runtime KG implementation authority", "engineering doc must preserve PRD-2 boundary"),
    ]:
        if phrase not in combined_text:
            errors.append(message)

    for key in TRUE_BOUNDARIES:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
    for key in FALSE_BOUNDARIES:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
    for key in [
        "required_check_classification_performed",
        "workflow_canonicalisation_performed",
        "ci_workflow_changes_performed",
        "openapi_reconciliation_performed",
    ]:
        if record.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in ["required_checks_enforced", "release_gate_enforced", "branch_protection_modified"]:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")

    authority_valid = not errors
    evidence_recorded = record.get("required_checks_workflow_release_gate_evidence_recorded") is True
    final_valid = (
        authority_valid
        and evidence_recorded
        and sequence_items_recorded(prd1_register)
        and prd1_5_authorised(prd1_register)
        and (
            (register.get("last_recorded_item") == "PRD-1.4" and register.get("next_authorised_item") == "PRD-1.5")
            or (register.get("last_recorded_item") == "PRD-1.9" and register.get("next_authorised_item") == "PRD-2")
        )
        and record.get("next_authorised_item") == "PRD-1.5"
        and record.get("prd1_5_authorised") is True
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-1.2-1.4 authority is valid but evidence capture has not completed")

    workflow_summary = live_config.get("workflow_canonicalisation", {}).get("workflow_summary_after_canonicalisation", {})
    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": ["PRD-1.2", "PRD-1.3", "PRD-1.4"],
        "stream_id": STREAM_ID,
        "errors": errors,
        "warnings": warnings,
        "prd101_ci_inventory_authority_valid": prd101.get("valid") is True,
        "required_check_classification_performed": record.get("required_check_classification_performed") is True,
        "workflow_canonicalisation_performed": record.get("workflow_canonicalisation_performed") is True,
        "ci_workflow_changes_performed": record.get("ci_workflow_changes_performed") is True,
        "openapi_reconciliation_performed": record.get("openapi_reconciliation_performed") is True,
        "required_checks_enforced": record.get("required_checks_enforced") is True,
        "release_gate_enforced": record.get("release_gate_enforced") is True,
        "branch_protection_modified": record.get("branch_protection_modified") is True,
        "required_checks_workflow_release_gate_evidence_recorded": evidence_recorded,
        "required_check_count": len(config.get("required_check_classification", {}).get("required_checks", [])),
        "python_m_pytest_workflow_count": workflow_summary.get("python_m_pytest_workflow_count"),
        "python3_m_pytest_workflow_count": workflow_summary.get("python3_m_pytest_workflow_count"),
        "openapi_root_and_docs_match": config.get("openapi_reconciliation", {}).get("root_and_docs_openapi_match") is True,
        "release_gate_defined": bool(config.get("release_gate_definition", {}).get("master_required_check_candidates")),
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "prd1_register_position": prd1_register_position(prd1_register),
        "prd1_5_authorised": record.get("prd1_5_authorised") is True,
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
        print(f"PRD-1.2-1.4 valid: {result['valid']}")
        print(f"PRD-1.2-1.4 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
