#!/usr/bin/env python3
"""Audit PRD-0.4 test/dependency bootstrap baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd003_documentation_housekeeping_ratchet_refresh import evaluate as evaluate_prd003

PRD_ID = "PRD-0.4"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_004_test_dependency_bootstrap_baseline.md"
PLAN = ROOT / "test_dependency_bootstrap_baseline_plan.md"
SCHEMA_DOC = ROOT / "test_dependency_bootstrap_baseline.schema.md"
RECORD = ROOT / "prd_004_test_dependency_bootstrap_baseline_record.json"
BASELINE = ROOT / "test_dependency_bootstrap_baseline.json"
REQUIRED_REQUIREMENT_FILES = [Path("requirements.txt"), Path("requirements-dev.txt"), Path("requirements/base.txt"), Path("requirements/dev.txt"), Path("requirements/constraints.snapshot.txt")]
PYTEST_CONFIG_FILES = [Path("pytest.ini"), Path("pytest-coverage.ini"), Path("pyproject.toml")]
FRONTEND_FILES = [Path("package.json"), Path("pnpm-lock.yaml"), Path("app/frontend/package.json")]
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]

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

def requirement_markers(root: Path) -> dict[str, bool]:
    dev = read_text(root / "requirements/dev.txt").lower()
    alias = read_text(root / "requirements-dev.txt")
    base_alias = read_text(root / "requirements.txt")
    return {
        "root_requirements_aliases_base": "-r requirements/base.txt" in base_alias,
        "root_dev_requirements_aliases_dev": "-r requirements/dev.txt" in alias,
        "pytest_declared": "pytest==" in dev or re.search(r"^pytest[<=>~]", dev, re.M) is not None,
        "pytest_cov_declared": "pytest-cov" in dev,
        "ruff_declared": "ruff" in dev or "ruff" in alias.lower(),
        "mypy_declared": "mypy" in dev or "mypy" in alias.lower(),
        "import_linter_declared": "import-linter" in dev or "import-linter" in alias.lower(),
    }

def frontend_markers(root: Path) -> dict[str, bool]:
    root_pkg = read_json(root / "package.json")
    frontend_pkg = read_json(root / "app/frontend/package.json")
    frontend_dev = frontend_pkg.get("devDependencies", {})
    frontend_scripts = frontend_pkg.get("scripts", {})
    return {
        "root_package_manager_pnpm": str(root_pkg.get("packageManager", "")).startswith("pnpm@"),
        "frontend_package_manager_pnpm": str(frontend_pkg.get("packageManager", "")).startswith("pnpm@"),
        "vitest_declared": "vitest" in frontend_dev,
        "playwright_declared_root": "@playwright/test" in root_pkg.get("devDependencies", {}),
        "frontend_test_script_recorded": "test" in frontend_scripts,
        "frontend_typecheck_script_recorded": "type-check" in frontend_scripts,
    }

def workflow_inventory(root: Path) -> dict[str, Any]:
    workflows = sorted((root / ".github/workflows").glob("*.yml")) + sorted((root / ".github/workflows").glob("*.yaml"))
    direct_pytest, module_pytest, dev_installs = [], [], []
    for wf in workflows:
        text = read_text(wf)
        rel = str(wf.relative_to(root))
        if re.search(r"(^|\s)pytest(\s|$)", text):
            direct_pytest.append(rel)
        if "python3 -m pytest" in text or "python -m pytest" in text:
            module_pytest.append(rel)
        if "requirements/dev.txt" in text or "requirements-dev.txt" in text:
            dev_installs.append(rel)
    return {"workflow_count": len(workflows), "direct_pytest_workflow_count": len(direct_pytest), "module_pytest_workflow_count": len(module_pytest), "dev_dependency_install_workflow_count": len(dev_installs), "direct_pytest_workflows": direct_pytest[:50], "module_pytest_workflows": module_pytest[:50], "dev_dependency_install_workflows": dev_installs[:50]}

def build_baseline(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": "prd-test-dependency-bootstrap/v1",
        "prd_id": PRD_ID,
        "captured_at": captured_at,
        "python_backend": {
            "requires_python": read_text(root / "pyproject.toml").split('requires-python = "')[1].split('"')[0] if 'requires-python = "' in read_text(root / "pyproject.toml") else None,
            "requirement_files": [{"path": str(path), "exists": (root / path).exists(), "sha256": sha256(root / path)} for path in REQUIRED_REQUIREMENT_FILES],
            "dependency_markers": requirement_markers(root),
            "pytest_config_files": [{"path": str(path), "exists": (root / path).exists(), "sha256": sha256(root / path)} for path in PYTEST_CONFIG_FILES],
        },
        "frontend": {
            "files": [{"path": str(path), "exists": (root / path).exists(), "sha256": sha256(root / path)} for path in FRONTEND_FILES],
            "dependency_markers": frontend_markers(root),
        },
        "workflow_inventory": workflow_inventory(root),
        "bootstrap_contracts": {
            "backend_test_command": "PYTHONPATH=. python3 -m pytest ...",
            "backend_dev_dependency_install": "pip install -r requirements.txt && pip install -r requirements/dev.txt",
            "frontend_install_command": "pnpm install --frozen-lockfile",
            "frontend_test_command": "pnpm test",
        },
        "deferred_to_later_prd0_slices": {"test_failure_collection_stabilisation": "PRD-0.5", "workflow_command_hygiene_convergence": "PRD-0.6", "openapi_generated_artifact_canonicalisation": "PRD-0.7"},
        "authority_boundaries": {"runtime_kg_implementation_claimed": True, "runtime_kg_authority_switch_authorised": True, "authority_switch_executed": True, "production_release_authorised": False, "deployment_authorised": False, "release_tag_authorised": False, "public_beta_authorised": False, "public_beta_live_traffic_authorised": False, "live_learner_traffic_authorised": False, "billing_launch_authorised": False, "live_payment_processing_authorised": False, "new_kg_slice_authorised": False, "prd1_implementation_authorised": False},
    }

def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    def p(path: Path) -> Path:
        return root / path
    prd003 = evaluate_prd003(root)
    prd003_valid = prd003.get("valid") is True
    if not prd003_valid:
        errors.append("PRD-0.3 documentation housekeeping ratchet refresh must be valid before PRD-0.4")
    for path in [REGISTER, PRD_DOC, PLAN, SCHEMA_DOC, RECORD, *REQUIRED_REQUIREMENT_FILES, *PYTEST_CONFIG_FILES, *FRONTEND_FILES]:
        if not p(path).exists():
            errors.append(f"missing PRD-0.4 required file: {path}")
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
    allowed_last = {f"PRD-0.{idx}" for idx in range(3, 11)} | {f"PRD-1.{idx}" for idx in range(0, 10)} | {f"PRD-{idx}" for idx in range(1, 12)} | {f"PRD-11.0R.RUNTIME-RESTORE.EXECUTION-{idx}" for idx in range(1, 10)}
    allowed_next = {f"PRD-0.{idx}" for idx in range(4, 11)} | {"PRD-1", "PRD-2"} | {f"PRD-1.{idx}" for idx in range(0, 10)} | {f"PRD-{idx}" for idx in range(1, 12)} | {f"PRD-11.0R.RUNTIME-RESTORE.EXECUTION-{idx}" for idx in range(1, 10)}
    if register.get("last_recorded_item") not in allowed_last:
        errors.append("production readiness register last_recorded_item must be PRD-0.3 or a later PRD-0 archival state")
    if register.get("next_authorised_item") not in allowed_next:
        errors.append("production readiness register next_authorised_item must be PRD-0.4 or a later authorised state")
    markers = requirement_markers(root)
    for key in ["root_requirements_aliases_base", "root_dev_requirements_aliases_dev", "pytest_declared", "pytest_cov_declared"]:
        if markers.get(key) is not True:
            errors.append(f"python dependency marker must be true: {key}")
    fmarkers = frontend_markers(root)
    for key in ["root_package_manager_pnpm", "frontend_package_manager_pnpm", "vitest_declared", "frontend_test_script_recorded"]:
        if fmarkers.get(key) is not True:
            errors.append(f"frontend dependency marker must be true: {key}")
    plan_text = read_text(p(PLAN))
    for phrase in ["PYTHONPATH=. python3 -m pytest", "PRD-0.5", "PRD-0.6", "PRD-0.7"]:
        if phrase not in plan_text:
            errors.append(f"PRD-0.4 plan must include phrase: {phrase}")
    record = read_json(p(RECORD))
    captured = record.get("test_dependency_bootstrap_baseline_recorded") is True
    baseline = read_json(p(BASELINE))
    if captured:
        for key in ["prd003_documentation_housekeeping_ratchet_refresh_valid", "dependency_manifest_recorded", "bootstrap_command_contract_recorded", "python_test_dependency_contract_recorded", "frontend_test_dependency_contract_recorded", "ci_dependency_install_contract_recorded", "deferred_failure_triage_boundary_recorded"]:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.4 record flag must be true: {key}")
        if baseline.get("schema_version") != "prd-test-dependency-bootstrap/v1":
            errors.append("captured PRD-0.4 baseline must use prd-test-dependency-bootstrap/v1")
        if baseline.get("prd_id") != PRD_ID:
            errors.append("captured PRD-0.4 baseline must identify PRD-0.4")
        if baseline.get("bootstrap_contracts", {}).get("backend_test_command") != "PYTHONPATH=. python3 -m pytest ...":
            errors.append("captured PRD-0.4 baseline must record python3 -m pytest backend test contract")
        if baseline.get("python_backend", {}).get("dependency_markers", {}).get("pytest_declared") is not True:
            errors.append("captured PRD-0.4 baseline must record pytest declared")
        if baseline.get("frontend", {}).get("dependency_markers", {}).get("vitest_declared") is not True:
            errors.append("captured PRD-0.4 baseline must record vitest declared")
        for key in TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.4 record must preserve true runtime KG flag: {key}")
        for key in FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"captured PRD-0.4 record boundary must remain false: {key}")
    else:
        warnings.append("PRD-0.4 evidence has not been captured yet")
    authority_errors = [error for error in errors if not error.startswith("captured PRD-0.4")]
    authority_valid = not authority_errors
    final_valid = authority_valid and captured and not errors
    winv = workflow_inventory(root)
    return {"authority_valid": authority_valid, "final_valid": final_valid, "recorded": captured, "prd_id": PRD_ID, "errors": errors, "warnings": warnings, "prd003_documentation_housekeeping_ratchet_refresh_valid": prd003_valid, "dependency_manifest_recorded": p(BASELINE).exists() or captured, "bootstrap_command_contract_recorded": "PYTHONPATH=. python3 -m pytest" in plan_text, "python_test_dependency_contract_recorded": markers.get("pytest_declared") is True, "frontend_test_dependency_contract_recorded": fmarkers.get("vitest_declared") is True, "ci_dependency_install_contract_recorded": captured or "requirements/dev.txt" in plan_text or "requirements/dev.txt" in json.dumps(winv), "deferred_failure_triage_boundary_recorded": "PRD-0.5" in plan_text, "requirements_file_count": sum(1 for path in REQUIRED_REQUIREMENT_FILES if p(path).exists()), "pytest_declared": markers.get("pytest_declared") is True, "pytest_cov_declared": markers.get("pytest_cov_declared") is True, "frontend_vitest_declared": fmarkers.get("vitest_declared") is True, "workflow_count": winv.get("workflow_count", 0), "direct_pytest_workflow_count": winv.get("direct_pytest_workflow_count", 0), "module_pytest_workflow_count": winv.get("module_pytest_workflow_count", 0), **{key: boundaries.get(key) for key in TRUE_KEYS + FALSE_KEYS}}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.4 authority valid: {result['authority_valid']}")
        print(f"PRD-0.4 final valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
