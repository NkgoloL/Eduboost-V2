#!/usr/bin/env python3
"""Audit PRD-0.8 branch/release naming reconciliation."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd007_openapi_generated_artifact_canonicalisation import evaluate as evaluate_prd007

PRD_ID = "PRD-0.8"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_008_branch_release_naming_reconciliation.md"
PLAN = ROOT / "branch_release_naming_reconciliation_plan.md"
SCHEMA_DOC = ROOT / "branch_release_naming_reconciliation.schema.md"
RECORD = ROOT / "prd_008_branch_release_naming_reconciliation_record.json"
INVENTORY = ROOT / "branch_release_naming_reconciliation.json"
BRANCHING_DOC = Path("docs/engineering/branching.md")
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def workflow_files(root: Path) -> list[Path]:
    base = root / ".github" / "workflows"
    if not base.exists():
        return []
    return sorted([*base.glob("*.yml"), *base.glob("*.yaml")])


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def branch_release_inventory(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    workflows = workflow_files(root)
    master_refs: list[str] = []
    main_refs: list[str] = []
    release_branch_refs: list[str] = []
    release_event_workflows: list[str] = []
    deployment_refs: list[str] = []
    for path in workflows:
        text = read_text(path)
        name = rel(root, path)
        if re.search(r"(?<![\w/-])master(?![\w/-])|refs/heads/master", text):
            master_refs.append(name)
        if re.search(r"(?<![\w/-])main(?![\w/-])|refs/heads/main", text):
            main_refs.append(name)
        if "release/**" in text or "refs/heads/release" in text or re.search(r"branches:\s*\[[^\]]*release/", text):
            release_branch_refs.append(name)
        if re.search(r"(^|\n)\s*release\s*:", text) or "release-candidate" in text or "release_candidate" in text:
            release_event_workflows.append(name)
        if re.search(r"deploy|deployment|production-promote|gh-pages|pages", text, flags=re.IGNORECASE):
            deployment_refs.append(name)
    branching_text = read_text(root / BRANCHING_DOC)
    stale_main_trunk = "`main` | Production-ready trunk" in branching_text or "main  ─" in branching_text
    canonical_master_doc = "`master` | Canonical protected trunk" in branching_text and "PRD-0.8" in branching_text
    return {
        "schema_version": "prd-branch-release-naming-reconciliation/v1",
        "prd_id": PRD_ID,
        "captured_at": captured_at,
        "canonical_trunk_branch": "master",
        "legacy_main_alias_policy": "compatibility-only; not current protected trunk",
        "release_branch_pattern": "release/**",
        "prd_authority_branch_pattern": "codex/prd-<nnn>-<slice-slug>",
        "prd_evidence_branch_pattern": "codex/prd-<nnn>-<slice-slug>-evidence",
        "branching_policy_document": str(BRANCHING_DOC),
        "branching_policy_document_refreshed": canonical_master_doc and not stale_main_trunk,
        "stale_main_trunk_claim_present": stale_main_trunk,
        "workflow_count": len(workflows),
        "workflow_branch_reference_summary": {
            "master_workflow_count": len(master_refs),
            "main_workflow_count": len(main_refs),
            "release_branch_workflow_count": len(release_branch_refs),
            "master_workflows": master_refs,
            "main_workflows": main_refs,
            "release_branch_workflows": release_branch_refs,
        },
        "release_event_workflow_count": len(release_event_workflows),
        "release_event_workflows": release_event_workflows,
        "deployment_reference_workflow_count": len(deployment_refs),
        "deployment_reference_workflows": deployment_refs,
        "reconciliation_policy": {
            "master_is_current_canonical_trunk": True,
            "main_is_legacy_compatibility_alias_only": True,
            "release_branches_do_not_authorise_release": True,
            "release_tags_blocked_until_later_prd_slice": True,
            "repository_hygiene_deferred_to_prd009": True,
        },
        "authority_boundaries": {
            "runtime_kg_implementation_claimed": True,
            "runtime_kg_authority_switch_authorised": True,
            "authority_switch_executed": True,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "public_beta_live_traffic_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
            "new_kg_slice_authorised": False,
            "prd1_implementation_authorised": False,
        },
    }


def audit(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    prd007 = evaluate_prd007(root)
    if not prd007.get("valid"):
        errors.append("PRD-0.7 OpenAPI/generated artifact canonicalisation must be valid before PRD-0.8")
    register = read_json(root / REGISTER)
    allowed_last = {"PRD-0.7", *{f"PRD-0.{idx}" for idx in range(8, 11)}, *{f"PRD-1.{idx}" for idx in range(0, 10)}}
    allowed_next = {"PRD-0.8", *{f"PRD-0.{idx}" for idx in range(9, 11)}, "PRD-1", "PRD-2", *{f"PRD-1.{idx}" for idx in range(0, 10)}}
    if register.get("last_recorded_item") not in allowed_last:
        errors.append("production readiness register last_recorded_item must be PRD-0.7 or a later PRD-0 archival state")
    if register.get("next_authorised_item") not in allowed_next:
        errors.append("production readiness register next_authorised_item must be PRD-0.8 or a later authorised state")
    for path in [PRD_DOC, PLAN, SCHEMA_DOC, RECORD]:
        if not (root / path).exists():
            errors.append(f"missing PRD-0.8 authority file: {path}")
    record = read_json(root / RECORD)
    inventory = read_json(root / INVENTORY)
    live_inventory = branch_release_inventory(root)
    current_inventory = inventory or live_inventory
    recorded = record.get("branch_release_naming_reconciliation_recorded") is True
    inventory_recorded = bool(inventory) and inventory.get("schema_version") == "prd-branch-release-naming-reconciliation/v1"
    branching_doc_ok = current_inventory.get("branching_policy_document_refreshed") is True
    for key in TRUE_KEYS:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
    for key in FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
    authority_valid = (
        not errors
        and record.get("prd007_openapi_generated_artifact_canonicalisation_valid") is True
        and record.get("canonical_trunk_branch_recorded") is True
        and record.get("canonical_trunk_branch") == "master"
        and record.get("legacy_main_alias_policy_recorded") is True
        and record.get("release_branch_pattern_recorded") is True
        and record.get("release_branch_pattern") == "release/**"
        and record.get("prd_authority_branch_pattern_recorded") is True
        and record.get("prd_evidence_branch_pattern_recorded") is True
        and record.get("release_tag_boundary_recorded") is True
        and record.get("production_release_boundary_recorded") is True
        and record.get("deployment_boundary_recorded") is True
        and record.get("no_release_authority_granted") is True
        and record.get("repository_hygiene_deferred_to_prd009") is True
        and branching_doc_ok
    )
    final_valid = (
        authority_valid
        and recorded
        and inventory_recorded
        and current_inventory.get("canonical_trunk_branch") == "master"
        and current_inventory.get("release_branch_pattern") == "release/**"
        and int(current_inventory.get("workflow_count") or 0) > 0
        and record.get("branch_release_inventory_recorded") is True
        and record.get("next_authorised_item") == "PRD-0.9"
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-0.8 authority is valid but evidence capture has not completed")
    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "errors": errors,
        "warnings": warnings,
        "prd007_openapi_generated_artifact_canonicalisation_valid": prd007.get("valid") is True,
        "branch_release_naming_reconciliation_recorded": recorded,
        "branch_release_inventory_recorded": record.get("branch_release_inventory_recorded") is True,
        "inventory_recorded": inventory_recorded,
        "canonical_trunk_branch_recorded": record.get("canonical_trunk_branch_recorded") is True,
        "canonical_trunk_branch": record.get("canonical_trunk_branch") or current_inventory.get("canonical_trunk_branch"),
        "legacy_main_alias_policy_recorded": record.get("legacy_main_alias_policy_recorded") is True,
        "release_branch_pattern_recorded": record.get("release_branch_pattern_recorded") is True,
        "release_branch_pattern": record.get("release_branch_pattern") or current_inventory.get("release_branch_pattern"),
        "branching_policy_document_refreshed": branching_doc_ok,
        "stale_main_trunk_claim_present": current_inventory.get("stale_main_trunk_claim_present") is True,
        "workflow_count": current_inventory.get("workflow_count", 0),
        "master_workflow_count": current_inventory.get("workflow_branch_reference_summary", {}).get("master_workflow_count", 0),
        "main_workflow_count": current_inventory.get("workflow_branch_reference_summary", {}).get("main_workflow_count", 0),
        "release_branch_workflow_count": current_inventory.get("workflow_branch_reference_summary", {}).get("release_branch_workflow_count", 0),
        "release_event_workflow_count": current_inventory.get("release_event_workflow_count", 0),
        "deployment_reference_workflow_count": current_inventory.get("deployment_reference_workflow_count", 0),
        "release_tag_boundary_recorded": record.get("release_tag_boundary_recorded") is True,
        "production_release_boundary_recorded": record.get("production_release_boundary_recorded") is True,
        "deployment_boundary_recorded": record.get("deployment_boundary_recorded") is True,
        "no_release_authority_granted": record.get("no_release_authority_granted") is True,
        "repository_hygiene_deferred_to_prd009": record.get("repository_hygiene_deferred_to_prd009") is True,
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed") is True,
        "runtime_kg_authority_switch_authorised": record.get("runtime_kg_authority_switch_authorised") is True,
        "authority_switch_executed": record.get("authority_switch_executed") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised") is True,
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True,
        "new_kg_slice_authorised": record.get("new_kg_slice_authorised") is True,
        "prd1_implementation_authorised": record.get("prd1_implementation_authorised") is True,
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
        print(f"PRD-0.8 valid: {result['valid']}")
        print(f"PRD-0.8 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
