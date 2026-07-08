#!/usr/bin/env python3
"""Audit PRD-0.6 workflow command hygiene and CI inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from scripts.production_readiness.apply_prd006_workflow_command_hygiene import is_direct_pytest_line
from scripts.roadmap_reconciliation.verify_prd005_test_failure_collection_stabilisation_register import evaluate as evaluate_prd005

PRD_ID = "PRD-0.6"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_006_workflow_command_hygiene_ci_inventory.md"
PLAN = ROOT / "workflow_command_hygiene_ci_inventory_plan.md"
SCHEMA_DOC = ROOT / "workflow_command_hygiene_ci_inventory.schema.md"
RECORD = ROOT / "prd_006_workflow_command_hygiene_ci_inventory_record.json"
WORKFLOW_INVENTORY = ROOT / "workflow_command_hygiene_ci_inventory.json"
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]
MODULE_PYTEST_RE = re.compile(r"python3?\s+-m\s+pytest")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def workflow_inventory(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    wf_root = root / ".github" / "workflows"
    workflows = sorted(wf_root.glob("*.yml")) + sorted(wf_root.glob("*.yaml")) if wf_root.exists() else []
    direct_commands: list[dict[str, Any]] = []
    module_commands: list[dict[str, Any]] = []
    dev_installs: list[str] = []
    workflows_with_pytest: set[str] = set()
    workflows_missing_dev_install: set[str] = set()
    per_workflow: list[dict[str, Any]] = []
    for wf in workflows:
        text = read_text(wf)
        rel = str(wf.relative_to(root))
        lines = text.splitlines()
        direct_line_numbers: list[int] = []
        module_line_numbers: list[int] = []
        for idx, line in enumerate(lines, start=1):
            if is_direct_pytest_line(line):
                direct_commands.append({"path": rel, "line": idx, "command": line.strip()})
                direct_line_numbers.append(idx)
            if MODULE_PYTEST_RE.search(line):
                module_commands.append({"path": rel, "line": idx, "command": line.strip()})
                module_line_numbers.append(idx)
        has_pytest = bool(direct_line_numbers or module_line_numbers)
        has_dev_install = "requirements/dev.txt" in text
        if has_dev_install:
            dev_installs.append(rel)
        if has_pytest:
            workflows_with_pytest.add(rel)
            if not has_dev_install:
                workflows_missing_dev_install.add(rel)
        per_workflow.append({
            "path": rel,
            "sha256": sha256(wf),
            "has_pytest": has_pytest,
            "direct_pytest_command_count": len(direct_line_numbers),
            "module_pytest_command_count": len(module_line_numbers),
            "has_requirements_dev_install": has_dev_install,
            "direct_pytest_lines": direct_line_numbers,
            "module_pytest_lines": module_line_numbers,
        })
    return {
        "schema_version": "prd-workflow-command-hygiene-ci-inventory/v1",
        "prd_id": PRD_ID,
        "captured_at": captured_at,
        "workflow_count": len(workflows),
        "pytest_workflow_count": len(workflows_with_pytest),
        "direct_pytest_command_count": len(direct_commands),
        "direct_pytest_workflow_count": len({item["path"] for item in direct_commands}),
        "module_pytest_command_count": len(module_commands),
        "module_pytest_workflow_count": len({item["path"] for item in module_commands}),
        "requirements_dev_install_workflow_count": len(dev_installs),
        "pytest_workflow_missing_dev_install_count": len(workflows_missing_dev_install),
        "direct_pytest_commands": direct_commands,
        "module_pytest_commands": module_commands[:200],
        "workflows_missing_dev_install": sorted(workflows_missing_dev_install),
        "workflow_files": per_workflow,
        "command_hygiene_policy": {
            "direct_pytest_invocations_allowed": False,
            "canonical_pytest_command": "PYTHONPATH=. python3 -m pytest",
            "dev_dependency_install_expected_for_pytest_workflows": True,
            "dependency_install_completion_deferred_to_ci_contract_review": True,
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
    prd005 = evaluate_prd005(root)
    if not prd005.get("valid"):
        errors.append("PRD-0.5 test failure and collection stabilisation register must be valid before PRD-0.6")
    register = read_json(root / REGISTER)
    allowed_last = {f"PRD-0.{idx}" for idx in range(5, 11)} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    allowed_next = {f"PRD-0.{idx}" for idx in range(6, 11)} | {"PRD-1"} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    if register.get("last_recorded_item") not in allowed_last:
        errors.append("production readiness register last_recorded_item must be PRD-0.5 or a later PRD-0 archival state")
    if register.get("next_authorised_item") not in allowed_next:
        errors.append("production readiness register next_authorised_item must be PRD-0.6 or a later authorised state")
    for path in [PRD_DOC, PLAN, SCHEMA_DOC, RECORD]:
        if not (root / path).exists():
            errors.append(f"missing PRD-0.6 authority file: {path}")
    record = read_json(root / RECORD)
    inventory = read_json(root / WORKFLOW_INVENTORY)
    live_inventory = workflow_inventory(root)
    recorded = record.get("workflow_command_hygiene_ci_inventory_recorded") is True
    inventory_recorded = bool(inventory) and inventory.get("schema_version") == "prd-workflow-command-hygiene-ci-inventory/v1"
    current_inventory = inventory or live_inventory
    direct_count = int(current_inventory.get("direct_pytest_command_count") or 0)
    module_count = int(current_inventory.get("module_pytest_command_count") or 0)
    workflow_count = int(current_inventory.get("workflow_count") or 0)
    dev_install_count = int(current_inventory.get("requirements_dev_install_workflow_count") or 0)
    direct_resolved = direct_count == 0
    canonical_recorded = record.get("canonical_pytest_command_recorded") is True or current_inventory.get("command_hygiene_policy", {}).get("canonical_pytest_command") == "PYTHONPATH=. python3 -m pytest"
    prd006_deferred_prd007 = record.get("openapi_generated_artifact_canonicalisation_deferred_to_prd007") is True
    prd006_deferred_prd008 = record.get("branch_release_naming_reconciliation_deferred_to_prd008") is True
    for key in TRUE_KEYS:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
    for key in FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
    final_valid = (
        not errors
        and recorded
        and inventory_recorded
        and workflow_count > 0
        and direct_resolved
        and module_count > 0
        and canonical_recorded
        and prd006_deferred_prd007
        and prd006_deferred_prd008
    )
    authority_valid = not errors
    return {
        "prd_id": PRD_ID,
        "errors": errors,
        "warnings": warnings,
        "authority_valid": authority_valid,
        "final_valid": final_valid,
        "recorded": recorded,
        "prd005_test_failure_collection_stabilisation_register_valid": prd005.get("valid") is True,
        "workflow_inventory_recorded": inventory_recorded,
        "workflow_count": workflow_count,
        "direct_pytest_command_count": direct_count,
        "direct_pytest_workflow_count": int(current_inventory.get("direct_pytest_workflow_count") or 0),
        "module_pytest_command_count": module_count,
        "module_pytest_workflow_count": int(current_inventory.get("module_pytest_workflow_count") or 0),
        "requirements_dev_install_workflow_count": dev_install_count,
        "pytest_workflow_missing_dev_install_count": int(current_inventory.get("pytest_workflow_missing_dev_install_count") or 0),
        "direct_pytest_commands_resolved": direct_resolved,
        "canonical_pytest_command_recorded": canonical_recorded,
        "ci_workflow_inventory_recorded": inventory_recorded,
        "openapi_generated_artifact_canonicalisation_deferred_to_prd007": prd006_deferred_prd007,
        "branch_release_naming_reconciliation_deferred_to_prd008": prd006_deferred_prd008,
        **{key: record.get(key) for key in TRUE_KEYS + FALSE_KEYS},
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
        print(f"PRD-0.6 authority_valid: {result['authority_valid']}")
        print(f"PRD-0.6 final_valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
