#!/usr/bin/env python3
"""Audit PRD-0.5 test failure and collection stabilisation register."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd004_test_dependency_bootstrap_baseline import evaluate as evaluate_prd004

PRD_ID = "PRD-0.5"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_005_test_failure_collection_stabilisation_register.md"
PLAN = ROOT / "test_failure_collection_stabilisation_plan.md"
SCHEMA_DOC = ROOT / "test_failure_collection_stabilisation.schema.md"
RECORD = ROOT / "prd_005_test_failure_collection_stabilisation_register_record.json"
STABILISATION_REGISTER = ROOT / "test_failure_collection_stabilisation_register.json"
PRD004_BASELINE = ROOT / "test_dependency_bootstrap_baseline.json"
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]
CLASSIFICATION_CATEGORIES = ["dependency_bootstrap", "import_or_collection", "stale_test_contract", "product_behavior", "external_service", "frontend_tooling", "environment_only", "documentation_or_generated_artifact"]


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


def discover_tests(root: Path) -> dict[str, Any]:
    tests_root = root / "tests"
    files = sorted(tests_root.rglob("test_*.py")) if tests_root.exists() else []
    by_top_level: dict[str, int] = {}
    function_count = 0
    class_count = 0
    parse_errors: list[dict[str, str]] = []
    for path in files:
        rel = path.relative_to(root)
        parts = rel.parts
        bucket = parts[1] if len(parts) > 1 else "root"
        by_top_level[bucket] = by_top_level.get(bucket, 0) + 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            parse_errors.append({"path": str(rel), "error": str(exc)})
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                function_count += 1
            elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                class_count += 1
    return {"test_file_count": len(files), "test_function_count": function_count, "test_class_count": class_count, "test_files_by_top_level": by_top_level, "python_parse_error_count": len(parse_errors), "python_parse_errors": parse_errors[:50], "sample_test_files": [str(path.relative_to(root)) for path in files[:50]]}


def discover_pytest_config(root: Path) -> dict[str, Any]:
    paths = [Path("pytest.ini"), Path("pytest-coverage.ini"), Path("pyproject.toml")]
    return {"pytest_config_files": [{"path": str(path), "exists": (root / path).exists(), "sha256": sha256(root / path)} for path in paths]}


def workflow_test_commands(root: Path) -> dict[str, Any]:
    wf_root = root / ".github" / "workflows"
    workflows = sorted(wf_root.glob("*.yml")) + sorted(wf_root.glob("*.yaml")) if wf_root.exists() else []
    direct_pytest: list[str] = []
    module_pytest: list[str] = []
    frontend_commands: list[str] = []
    for wf in workflows:
        text = read_text(wf)
        rel = str(wf.relative_to(root))
        if re.search(r"(^|\s)pytest(\s|$)", text):
            direct_pytest.append(rel)
        if "python3 -m pytest" in text or "python -m pytest" in text:
            module_pytest.append(rel)
        if "pnpm test" in text or "vitest" in text or "playwright" in text:
            frontend_commands.append(rel)
    return {"workflow_count": len(workflows), "direct_pytest_workflow_count": len(direct_pytest), "module_pytest_workflow_count": len(module_pytest), "frontend_test_workflow_count": len(frontend_commands), "direct_pytest_workflows": direct_pytest[:80], "module_pytest_workflows": module_pytest[:80], "frontend_test_workflows": frontend_commands[:80]}


def command_matrix() -> list[dict[str, Any]]:
    return [
        {"command_id": "backend_control_plane_prd_tests", "command": "PYTHONPATH=. python3 -m pytest -q tests/unit/roadmap_reconciliation --no-cov", "purpose": "control-plane verifier regression tests", "classification_if_failing": "stale_test_contract", "execution_required_in_prd005": False},
        {"command_id": "backend_unit_collection", "command": "PYTHONPATH=. python3 -m pytest --collect-only -q tests/unit --no-cov", "purpose": "unit test collection baseline", "classification_if_failing": "import_or_collection", "execution_required_in_prd005": False},
        {"command_id": "backend_full_collection", "command": "PYTHONPATH=. python3 -m pytest --collect-only -q tests --no-cov", "purpose": "full Python test collection baseline", "classification_if_failing": "import_or_collection", "execution_required_in_prd005": False},
        {"command_id": "backend_smoke_import", "command": "PYTHONPATH=. python3 -m pytest -q tests/smoke/test_app_import.py --no-cov", "purpose": "application import smoke baseline", "classification_if_failing": "dependency_bootstrap", "execution_required_in_prd005": False},
        {"command_id": "frontend_unit_tests", "command": "pnpm test", "purpose": "frontend unit test baseline", "classification_if_failing": "frontend_tooling", "execution_required_in_prd005": False},
        {"command_id": "frontend_e2e_opt_in", "command": "npx playwright test", "purpose": "frontend e2e opt-in command contract", "classification_if_failing": "frontend_tooling", "execution_required_in_prd005": False},
        {"command_id": "docs_housekeeping", "command": "make docs-housekeeping-check", "purpose": "documentation ratchet regression baseline", "classification_if_failing": "documentation_or_generated_artifact", "execution_required_in_prd005": False},
    ]


def build_stabilisation_register(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    prd004 = read_json(root / PRD004_BASELINE)
    tests = discover_tests(root)
    workflows = workflow_test_commands(root)
    categories = [{"category": category, "owner_slice": "PRD-0.5", "allowed_action": "classify_and_register_before_repair"} for category in CLASSIFICATION_CATEGORIES]
    triage_register = [
        {"triage_id": "PRD005-TRIAGE-001", "title": "Python test collection baseline", "status": "registered_for_stabilisation", "category": "import_or_collection", "reproduction_command_id": "backend_full_collection", "repair_slice": "PRD-0.5-or-later", "delete_tests_authorised": False},
        {"triage_id": "PRD005-TRIAGE-002", "title": "Smoke import/dependency bootstrap baseline", "status": "registered_for_stabilisation", "category": "dependency_bootstrap", "reproduction_command_id": "backend_smoke_import", "repair_slice": "PRD-0.5-or-later", "delete_tests_authorised": False},
        {"triage_id": "PRD005-TRIAGE-003", "title": "Frontend unit/e2e command baseline", "status": "registered_for_stabilisation", "category": "frontend_tooling", "reproduction_command_id": "frontend_unit_tests", "repair_slice": "PRD-0.6-or-later", "delete_tests_authorised": False},
        {"triage_id": "PRD005-TRIAGE-004", "title": "Workflow pytest command convergence", "status": "registered_for_prd006", "category": "environment_only", "reproduction_command_id": "backend_control_plane_prd_tests", "repair_slice": "PRD-0.6", "delete_tests_authorised": False},
        {"triage_id": "PRD005-TRIAGE-005", "title": "Generated documentation artifact drift", "status": "registered_for_prd007_or_housekeeping", "category": "documentation_or_generated_artifact", "reproduction_command_id": "docs_housekeeping", "repair_slice": "PRD-0.7-or-later", "delete_tests_authorised": False},
    ]
    return {
        "schema_version": "prd-test-failure-collection-stabilisation/v1",
        "prd_id": PRD_ID,
        "captured_at": captured_at,
        "upstream_baseline": {"prd004_baseline_present": bool(prd004), "prd004_schema_version": prd004.get("schema_version"), "prd004_workflow_count": prd004.get("workflow_inventory", {}).get("workflow_count"), "prd004_direct_pytest_workflow_count": prd004.get("workflow_inventory", {}).get("direct_pytest_workflow_count")},
        "test_inventory": tests,
        "pytest_configuration": discover_pytest_config(root),
        "workflow_test_command_inventory": workflows,
        "collection_command_matrix": command_matrix(),
        "failure_classification_schema": categories,
        "triage_register": triage_register,
        "stabilisation_boundaries": {"no_test_deletions_authorised": True, "no_silent_xfail_authorised": True, "no_product_behavior_repairs_authorised": True, "broad_test_execution_repairs_deferred": True, "workflow_command_hygiene_deferred_to_prd006": True, "openapi_generated_artifact_canonicalisation_deferred_to_prd007": True},
        "authority_boundaries": {"runtime_kg_implementation_claimed": True, "runtime_kg_authority_switch_authorised": True, "authority_switch_executed": True, "production_release_authorised": False, "deployment_authorised": False, "release_tag_authorised": False, "public_beta_authorised": False, "public_beta_live_traffic_authorised": False, "live_learner_traffic_authorised": False, "billing_launch_authorised": False, "live_payment_processing_authorised": False, "new_kg_slice_authorised": False, "prd1_implementation_authorised": False},
    }


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    def p(path: Path) -> Path:
        return root / path
    prd004 = evaluate_prd004(root)
    prd004_valid = prd004.get("valid") is True
    if not prd004_valid:
        errors.append("PRD-0.4 test/dependency bootstrap baseline must be valid before PRD-0.5")
    for path in [REGISTER, PRD_DOC, PLAN, SCHEMA_DOC, RECORD]:
        if not p(path).exists():
            errors.append(f"missing PRD-0.5 required file: {path}")
    register = read_json(p(REGISTER))
    boundaries = register.get("authority_boundaries", {})
    if register.get("stream_id") != "PRD-PRODUCTION-READINESS":
        errors.append("production readiness register must identify PRD-PRODUCTION-READINESS")
    for key in TRUE_KEYS:
        if boundaries.get(key) is not True:
            errors.append(f"register boundary must preserve true runtime KG flag: {key}")
    for key in FALSE_KEYS:
        if boundaries.get(key) is not False:
            errors.append(f"register boundary must keep false: {key}")
    allowed_last = {"PRD-0.4", *{f"PRD-0.{idx}" for idx in range(5, 11)}, *{f"PRD-1.{idx}" for idx in range(0, 10)}}
    allowed_next = {"PRD-0.5", *{f"PRD-0.{idx}" for idx in range(6, 11)}, "PRD-1", "PRD-2", *{f"PRD-1.{idx}" for idx in range(0, 10)}}
    if register.get("last_recorded_item") not in allowed_last:
        errors.append("production readiness register last_recorded_item must be PRD-0.4 or a later PRD-0 archival state")
    if register.get("next_authorised_item") not in allowed_next:
        errors.append("production readiness register next_authorised_item must be PRD-0.5 or a later authorised state")
    plan_text = read_text(p(PLAN))
    for phrase in ["test failure", "collection", "classification", "PRD-0.6", "no silent deletion"]:
        if phrase not in plan_text:
            errors.append(f"PRD-0.5 plan must include phrase: {phrase}")
    record = read_json(p(RECORD))
    recorded = record.get("test_failure_collection_stabilisation_register_recorded") is True
    stabilisation = read_json(p(STABILISATION_REGISTER))
    if recorded:
        for key in ["prd004_test_dependency_bootstrap_baseline_valid", "test_inventory_recorded", "collection_command_matrix_recorded", "failure_classification_schema_recorded", "triage_register_recorded", "no_test_deletions_authorised", "workflow_hygiene_deferred_to_prd006"]:
            if record.get(key) is not True:
                errors.append(f"record must mark {key} true after capture")
        if stabilisation.get("schema_version") != "prd-test-failure-collection-stabilisation/v1":
            errors.append("test failure collection stabilisation register must use schema v1")
        if stabilisation.get("test_inventory", {}).get("test_file_count", 0) <= 0:
            errors.append("test inventory must record at least one test file")
        if len(stabilisation.get("collection_command_matrix", [])) < 5:
            errors.append("collection command matrix must include at least five commands")
        categories = {item.get("category") for item in stabilisation.get("failure_classification_schema", [])}
        for category in CLASSIFICATION_CATEGORIES:
            if category not in categories:
                errors.append(f"failure classification schema missing category: {category}")
        if len(stabilisation.get("triage_register", [])) < 5:
            errors.append("triage register must include at least five baseline triage entries")
        bounds = stabilisation.get("stabilisation_boundaries", {})
        for key in ["no_test_deletions_authorised", "no_silent_xfail_authorised", "no_product_behavior_repairs_authorised", "workflow_command_hygiene_deferred_to_prd006"]:
            if bounds.get(key) is not True:
                errors.append(f"stabilisation boundary must be true: {key}")
    else:
        if p(STABILISATION_REGISTER).exists():
            warnings.append("test failure collection stabilisation register exists before capture")
    result = {
        "prd_id": PRD_ID,
        "authority_valid": not errors,
        "recorded": recorded,
        "final_valid": recorded and not errors,
        "errors": errors,
        "warnings": warnings,
        "prd004_test_dependency_bootstrap_baseline_valid": prd004_valid,
        "test_inventory_recorded": record.get("test_inventory_recorded") is True if recorded else False,
        "collection_command_matrix_recorded": record.get("collection_command_matrix_recorded") is True if recorded else False,
        "failure_classification_schema_recorded": record.get("failure_classification_schema_recorded") is True if recorded else False,
        "triage_register_recorded": record.get("triage_register_recorded") is True if recorded else False,
        "test_file_count": record.get("test_file_count", 0),
        "test_function_count": record.get("test_function_count", 0),
        "collection_command_count": record.get("collection_command_count", 0),
        "triage_item_count": record.get("triage_item_count", 0),
        "no_test_deletions_authorised": record.get("no_test_deletions_authorised") is True if recorded else True,
        "workflow_hygiene_deferred_to_prd006": record.get("workflow_hygiene_deferred_to_prd006") is True if recorded else True,
    }
    for key in TRUE_KEYS + FALSE_KEYS:
        result[key] = record.get(key) if recorded else boundaries.get(key)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.5 audit authority_valid: {result['authority_valid']}")
        print(f"PRD-0.5 audit final_valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
