#!/usr/bin/env python3
"""Audit PRD-1.1 CI inventory authority."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd100_ci_release_gate_stream_authority import evaluate as evaluate_prd100

PRD_ID = "PRD-1.1"
STREAM_ID = "PRD-1-CI-RELEASE-GATE-CONVERGENCE"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD1_REGISTER = ROOT / "prd1_ci_release_gate_register.json"
PRD_DOC = ROOT / "prd_101_ci_inventory_authority.md"
PLAN = ROOT / "prd1_ci_inventory_authority_plan.md"
SCHEMA_DOC = ROOT / "prd1_ci_inventory_authority.schema.md"
RECORD = ROOT / "prd_101_ci_inventory_authority_record.json"
SNAPSHOT = ROOT / "prd1_ci_inventory_authority.json"
ENGINEERING_DOC = Path("docs/engineering/prd1_ci_inventory_authority.md")

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
    "required_check_classification_performed",
]

WORKFLOW_SUFFIXES = {".yml", ".yaml"}
CI_TERMS = ["pytest", "coverage", "py_compile", "ruff", "mypy", "playwright", "docker", "openapi", "alembic"]
DEPLOYMENT_TERMS = ["deploy", "deployment", "promotion", "production", "environment", "release"]
BRANCH_PROTECTION_TERMS = ["branch protection", "required check", "required_checks", "required status", "status check"]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def bool_find(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) is not None


def workflow_inventory(root: Path) -> list[dict[str, Any]]:
    workflow_root = root / ".github" / "workflows"
    items: list[dict[str, Any]] = []
    if not workflow_root.exists():
        return items
    for path in sorted(p for p in workflow_root.iterdir() if p.is_file() and p.suffix in WORKFLOW_SUFFIXES):
        text = read_text(path)
        lower = text.lower()
        items.append({
            "path": path.as_posix(),
            "line_count": len(text.splitlines()),
            "mentions_master": "master" in lower,
            "mentions_main": bool_find(r"(^|[^a-z0-9_-])main([^a-z0-9_-]|$)", text),
            "mentions_release_branch": "release/" in lower or "release/**" in lower,
            "mentions_release_event": bool_find(r"on:\s*release|types:\s*\[[^\]]*published|release:", text),
            "mentions_deployment_or_promotion": any(term in lower for term in DEPLOYMENT_TERMS),
            "mentions_openapi": "openapi" in lower,
            "mentions_pytest": "pytest" in lower,
            "uses_python_m_pytest": "python -m pytest" in lower,
            "uses_python3_m_pytest": "python3 -m pytest" in lower,
            "ci_terms": sorted(term for term in CI_TERMS if term in lower),
        })
    return items


def makefile_inventory(root: Path) -> dict[str, Any]:
    path = root / "Makefile"
    text = read_text(path)
    targets: list[str] = []
    for line in text.splitlines():
        if line and not line.startswith(("\t", " ", "#")) and ":" in line:
            name = line.split(":", 1)[0].strip()
            if name and not name.startswith("."):
                targets.append(name)
    lower = text.lower()
    return {
        "path": "Makefile",
        "exists": path.exists(),
        "target_count": len(targets),
        "ci_like_target_count": sum(1 for target in targets if any(term in target.lower() for term in ["test", "pytest", "ci", "check", "verify", "prd"])),
        "targets_sample": targets[:75],
        "mentions_pytest": "pytest" in lower,
        "uses_python_m_pytest": "python -m pytest" in lower,
        "uses_python3_m_pytest": "python3 -m pytest" in lower,
        "mentions_openapi": "openapi" in lower,
    }


def openapi_inventory(root: Path) -> dict[str, Any]:
    paths = [Path("openapi.json"), Path("docs/openapi.json")]
    return {
        "paths": [
            {"path": path.as_posix(), "exists": (root / path).exists(), "size_bytes": (root / path).stat().st_size if (root / path).exists() else None}
            for path in paths
        ],
        "root_openapi_present": (root / "openapi.json").exists(),
        "docs_openapi_present": (root / "docs" / "openapi.json").exists(),
    }


def branch_protection_inventory(root: Path) -> dict[str, Any]:
    refs: list[dict[str, Any]] = []
    search_roots = [root / "docs", root / ".github"]
    for base in search_roots:
        if not base.exists():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".json", ".yml", ".yaml"}):
            rel = path.relative_to(root).as_posix()
            text = read_text(path)
            lower = text.lower()
            matched = sorted(term for term in BRANCH_PROTECTION_TERMS if term in lower)
            if matched:
                refs.append({"path": rel, "matched_terms": matched})
    return {"reference_count": len(refs), "references": refs[:100]}


def collect_ci_inventory(root: Path = Path("."), captured_at: str | None = None) -> dict[str, Any]:
    workflows = workflow_inventory(root)
    makefile = makefile_inventory(root)
    openapi = openapi_inventory(root)
    branch_protection = branch_protection_inventory(root)
    summary = {
        "workflow_count": len(workflows),
        "master_workflow_count": sum(1 for item in workflows if item["mentions_master"]),
        "main_workflow_count": sum(1 for item in workflows if item["mentions_main"]),
        "release_branch_workflow_count": sum(1 for item in workflows if item["mentions_release_branch"]),
        "release_event_workflow_count": sum(1 for item in workflows if item["mentions_release_event"]),
        "deployment_reference_workflow_count": sum(1 for item in workflows if item["mentions_deployment_or_promotion"]),
        "openapi_reference_workflow_count": sum(1 for item in workflows if item["mentions_openapi"]),
        "pytest_reference_workflow_count": sum(1 for item in workflows if item["mentions_pytest"]),
        "python_m_pytest_workflow_count": sum(1 for item in workflows if item["uses_python_m_pytest"]),
        "python3_m_pytest_workflow_count": sum(1 for item in workflows if item["uses_python3_m_pytest"]),
        "makefile_ci_like_target_count": makefile["ci_like_target_count"],
        "branch_protection_reference_count": branch_protection["reference_count"],
        "root_openapi_present": openapi["root_openapi_present"],
        "docs_openapi_present": openapi["docs_openapi_present"],
    }
    return {
        "schema_version": "prd1-ci-inventory-authority/v1",
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "captured_at": captured_at,
        "workflow_inventory": workflows,
        "makefile_inventory": makefile,
        "openapi_inventory": openapi,
        "branch_protection_inventory": branch_protection,
        "summary": summary,
        "authority_boundaries": {**{key: True for key in TRUE_KEYS}, **{key: False for key in FALSE_KEYS}},
        "implementation_boundaries": {key: False for key in NO_CHANGE_KEYS},
        "next_authorised_item": "PRD-1.2",
    }


def prd1_1_recorded(prd1_register: dict[str, Any]) -> bool:
    last_item = prd1_register.get("last_recorded_item")
    next_item = prd1_register.get("next_authorised_item")
    if (last_item, next_item) not in {
        (PRD_ID, "PRD-1.2"),
        ("PRD-1.4", "PRD-1.5"),
        ("PRD-1.9", "PRD-2"),
        ("PRD-1.9", "PRD-3"),
    }:
        return False
    return any(
        item.get("prd_id") == PRD_ID and item.get("authorised") is True and item.get("status") == "recorded"
        for item in prd1_register.get("prd1_sequence", [])
    )


def production_register_position(register: dict[str, Any]) -> str:
    last_item = register.get("last_recorded_item")
    next_item = register.get("next_authorised_item")
    if last_item == "PRD-1.0" and next_item == PRD_ID:
        return "after_prd1_0_before_prd1_1_capture"
    if last_item == PRD_ID and next_item == "PRD-1.2":
        return "prd1_1_recorded"
    if last_item == "PRD-1.4" and next_item == "PRD-1.5":
        return "prd1_4_recorded_after_prd1_1"
    if last_item == "PRD-1.9" and next_item in {"PRD-2", "PRD-3"}:
        return "prd1_closed_after_prd1_1"
    if str(last_item).startswith("PRD-2.") and next_item == "PRD-3":
        return "prd1_closed_after_prd1_1"
    return "unexpected"


def inventory_snapshot(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    register = read_json(root / REGISTER)
    prd1_register = read_json(root / PRD1_REGISTER)
    inventory = collect_ci_inventory(root, captured_at=captured_at)
    inventory["production_readiness_register_summary"] = {
        "last_recorded_item": register.get("last_recorded_item"),
        "next_authorised_item": register.get("next_authorised_item"),
        "position": production_register_position(register),
    }
    inventory["prd1_register_summary"] = {
        "last_recorded_item": prd1_register.get("last_recorded_item"),
        "next_authorised_item": prd1_register.get("next_authorised_item"),
        "prd1_1_recorded": prd1_1_recorded(prd1_register),
    }
    return inventory


def audit(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    register = read_json(root / REGISTER)
    prd1_register = read_json(root / PRD1_REGISTER)
    record = read_json(root / RECORD)
    saved_snapshot = read_json(root / SNAPSHOT)
    live_snapshot = inventory_snapshot(root)
    prd100 = evaluate_prd100(root)

    for path in [PRD_DOC, PLAN, SCHEMA_DOC, RECORD, ENGINEERING_DOC]:
        if not (root / path).exists():
            errors.append(f"missing required PRD-1.1 file: {path}")

    if prd100.get("valid") is not True:
        errors.append("PRD-1.0 verifier must remain valid before PRD-1.1")
    if production_register_position(register) == "unexpected":
        errors.append("production readiness register must be positioned at PRD-1.0/PRD-1.1, PRD-1.1/PRD-1.2, PRD-1.4/PRD-1.5, or PRD-1.9/PRD-2")
    if prd1_register.get("schema_version") != "prd1-ci-release-gate-register/v1":
        errors.append("PRD-1 register schema_version must remain prd1-ci-release-gate-register/v1")
    if prd1_register.get("stream_id") != STREAM_ID:
        errors.append("PRD-1 register stream_id must remain canonical")

    required_text = [
        (read_text(root / PRD_DOC), "inventory-only", "PRD-1.1 doc must preserve inventory-only boundary"),
        (read_text(root / PRD_DOC), "PRD-1.2 — Required Check Classification", "PRD-1.1 doc must identify PRD-1.2 as next slice"),
        (read_text(root / PLAN), "last_recorded_item", "PRD-1.1 plan must describe terminal register state"),
        (read_text(root / SCHEMA_DOC), "prd1-ci-inventory-authority/v1", "PRD-1.1 schema must define inventory version"),
        (read_text(root / ENGINEERING_DOC), "Runtime KG implementation remains reserved for PRD-2", "engineering doc must preserve PRD-2 boundary"),
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
    for key in NO_CHANGE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false in PRD-1.1")

    for key in [
        "no_required_check_classification_performed",
        "no_workflow_canonicalisation_performed",
        "no_ci_workflow_changes_performed",
        "no_required_check_enforcement_performed",
        "no_release_gate_enforcement_performed",
        "no_branch_protection_change_performed",
        "no_openapi_reconciliation_performed",
        "no_prd2_implementation_performed",
    ]:
        if record.get(key) is not True:
            errors.append(f"{key} must be true")

    if live_snapshot.get("summary", {}).get("workflow_count", 0) <= 0:
        errors.append("CI inventory must include at least one workflow")
    if "makefile_inventory" not in live_snapshot:
        errors.append("CI inventory must include Makefile inventory")
    if "openapi_inventory" not in live_snapshot:
        errors.append("CI inventory must include OpenAPI inventory")

    authority_valid = not errors
    recorded = record.get("ci_inventory_authority_recorded") is True and record.get("ci_inventory_evidence_recorded") is True
    snapshot_recorded = (
        saved_snapshot.get("schema_version") == "prd1-ci-inventory-authority/v1"
        and saved_snapshot.get("prd_id") == PRD_ID
        and saved_snapshot.get("summary", {}).get("workflow_count", 0) > 0
    )
    inventory_count_matches = (
        snapshot_recorded
        and saved_snapshot.get("summary", {}).get("workflow_count") == live_snapshot.get("summary", {}).get("workflow_count")
    )
    final_valid = (
        authority_valid
        and recorded
        and snapshot_recorded
        and inventory_count_matches
        and prd1_1_recorded(prd1_register)
        and production_register_position(register) in {"prd1_1_recorded", "prd1_4_recorded_after_prd1_1", "prd1_closed_after_prd1_1"}
        and record.get("next_authorised_item") in {"PRD-1.2", "PRD-1.5", "PRD-2"}
        and record.get("prd1_2_authorised") is True
        and record.get("ci_inventory_performed") is True
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-1.1 authority is valid but evidence capture has not completed")

    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "stream_id": STREAM_ID,
        "errors": errors,
        "warnings": warnings,
        "prd100_ci_release_gate_stream_authority_valid": prd100.get("valid") is True,
        "ci_inventory_authority_recorded": record.get("ci_inventory_authority_recorded") is True,
        "ci_inventory_evidence_recorded": record.get("ci_inventory_evidence_recorded") is True,
        "ci_inventory_recorded": record.get("ci_inventory_recorded") is True,
        "ci_inventory_performed": record.get("ci_inventory_performed") is True,
        "snapshot_recorded": snapshot_recorded,
        "inventory_count_matches": inventory_count_matches,
        "workflow_count": live_snapshot.get("summary", {}).get("workflow_count"),
        "master_workflow_count": live_snapshot.get("summary", {}).get("master_workflow_count"),
        "main_workflow_count": live_snapshot.get("summary", {}).get("main_workflow_count"),
        "release_branch_workflow_count": live_snapshot.get("summary", {}).get("release_branch_workflow_count"),
        "release_event_workflow_count": live_snapshot.get("summary", {}).get("release_event_workflow_count"),
        "deployment_reference_workflow_count": live_snapshot.get("summary", {}).get("deployment_reference_workflow_count"),
        "openapi_reference_workflow_count": live_snapshot.get("summary", {}).get("openapi_reference_workflow_count"),
        "pytest_reference_workflow_count": live_snapshot.get("summary", {}).get("pytest_reference_workflow_count"),
        "python_m_pytest_workflow_count": live_snapshot.get("summary", {}).get("python_m_pytest_workflow_count"),
        "python3_m_pytest_workflow_count": live_snapshot.get("summary", {}).get("python3_m_pytest_workflow_count"),
        "makefile_ci_like_target_count": live_snapshot.get("summary", {}).get("makefile_ci_like_target_count"),
        "branch_protection_reference_count": live_snapshot.get("summary", {}).get("branch_protection_reference_count"),
        "root_openapi_present": live_snapshot.get("summary", {}).get("root_openapi_present"),
        "docs_openapi_present": live_snapshot.get("summary", {}).get("docs_openapi_present"),
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_position": production_register_position(register),
        "prd1_2_authorised": record.get("prd1_2_authorised") is True,
        "no_required_check_classification_performed": record.get("no_required_check_classification_performed") is True,
        "no_workflow_canonicalisation_performed": record.get("no_workflow_canonicalisation_performed") is True,
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
        print(f"PRD-1.1 valid: {result['valid']}")
        print(f"PRD-1.1 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
