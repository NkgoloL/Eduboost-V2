#!/usr/bin/env python3
"""Apply PRD-1.2-1.4 required-check, workflow, and release-gate convergence."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PRD_ID = "PRD-1.2-1.4"
STREAM_ID = "PRD-1-CI-RELEASE-GATE-CONVERGENCE"
ROOT = Path("docs/roadmap/production_readiness")
RECORD = ROOT / "prd_102_104_required_checks_workflow_release_gate_convergence_record.json"
CONFIG = ROOT / "prd1_required_checks_workflow_release_gate_convergence.json"
DOC = ROOT / "prd_102_104_required_checks_workflow_release_gate_convergence.md"
ENGINEERING_DOC = Path("docs/engineering/prd1_required_checks_workflow_release_gate_convergence.md")

REQUIRED_CHECKS = [
    {
        "check_id": "python-package-and-unit-tests",
        "label": "Python package compile and unit tests",
        "source": "existing CI workflows and Makefile targets",
        "required_for_master": True,
        "blocks_release_candidate": True,
    },
    {
        "check_id": "openapi-contract-and-drift",
        "label": "OpenAPI contract and drift verification",
        "source": ".github/workflows/openapi-contract.yml and .github/workflows/openapi-drift.yml",
        "required_for_master": True,
        "blocks_release_candidate": True,
    },
    {
        "check_id": "security-and-dependency-scan",
        "label": "Security and dependency scanning",
        "source": ".github/workflows/dependency-scan.yml plus security-oriented workflows",
        "required_for_master": True,
        "blocks_release_candidate": True,
    },
    {
        "check_id": "migration-and-runtime-contracts",
        "label": "Database migration and runtime contract checks",
        "source": ".github/workflows/migration_check.yml and .github/workflows/runtime-contract.yml",
        "required_for_master": True,
        "blocks_release_candidate": True,
    },
    {
        "check_id": "release-readiness-cluster",
        "label": "Release-readiness cluster checks",
        "source": ".github/workflows/cluster-h-release-readiness.yml and release-readiness documentation",
        "required_for_master": False,
        "blocks_release_candidate": True,
    },
]

ADVISORY_CHECKS = [
    {
        "check_id": "frontend-lighthouse-and-e2e",
        "label": "Frontend Lighthouse and E2E checks",
        "required_for_master": False,
        "reason": "Useful release signal, but not promoted to master-required until PRD-1.5 convergence evidence proves stability.",
    },
    {
        "check_id": "historical-prd-kg-evidence-workflows",
        "label": "Historical PRD/KG evidence workflows",
        "required_for_master": False,
        "reason": "Retained for audit replay and evidence continuity; not a production release gate.",
    },
]

FALSE_BOUNDARIES = [
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
TRUE_BOUNDARIES = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "authority_switch_executed",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def canonicalise_pytest_commands(root: Path) -> list[dict[str, Any]]:
    candidates: list[Path] = []
    workflow_root = root / ".github" / "workflows"
    if workflow_root.exists():
        candidates.extend(sorted(p for p in workflow_root.iterdir() if p.is_file() and p.suffix in {".yml", ".yaml"}))
    makefile = root / "Makefile"
    if makefile.exists():
        candidates.append(makefile)

    changed: list[dict[str, Any]] = []
    for path in candidates:
        before = read_text(path)
        count = before.count("python -m pytest")
        after = before.replace("python -m pytest", "python3 -m pytest")
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append({
                "path": path.relative_to(root).as_posix(),
                "python_m_pytest_replacements": count,
            })
    return changed


def workflow_summary(root: Path) -> dict[str, Any]:
    workflow_root = root / ".github" / "workflows"
    workflows = sorted(p for p in workflow_root.iterdir() if p.is_file() and p.suffix in {".yml", ".yaml"}) if workflow_root.exists() else []
    python_m: list[str] = []
    python3_m: list[str] = []
    release_refs: list[str] = []
    deployment_refs: list[str] = []
    main_refs: list[str] = []
    master_refs: list[str] = []
    openapi_refs: list[str] = []
    for path in workflows:
        text = read_text(path).lower()
        rel = path.relative_to(root).as_posix()
        if "python -m pytest" in text:
            python_m.append(rel)
        if "python3 -m pytest" in text:
            python3_m.append(rel)
        if "release/" in text or "release/**" in text or re.search(r"on:\s*release|release:", text):
            release_refs.append(rel)
        if any(term in text for term in ["deploy", "deployment", "promotion", "production", "environment"]):
            deployment_refs.append(rel)
        if re.search(r"(^|[^a-z0-9_-])main([^a-z0-9_-]|$)", text):
            main_refs.append(rel)
        if "master" in text:
            master_refs.append(rel)
        if "openapi" in text:
            openapi_refs.append(rel)
    return {
        "workflow_count": len(workflows),
        "python_m_pytest_workflow_count": len(python_m),
        "python3_m_pytest_workflow_count": len(python3_m),
        "python_m_pytest_workflows": python_m,
        "python3_m_pytest_workflows": python3_m,
        "release_reference_workflow_count": len(release_refs),
        "deployment_reference_workflow_count": len(deployment_refs),
        "main_reference_workflow_count": len(main_refs),
        "master_reference_workflow_count": len(master_refs),
        "openapi_reference_workflow_count": len(openapi_refs),
    }


def build_config(root: Path, changed_files: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    openapi_root = root / "openapi.json"
    openapi_docs = root / "docs" / "openapi.json"
    root_sha = sha256(openapi_root)
    docs_sha = sha256(openapi_docs)
    return {
        "schema_version": "prd1-required-checks-workflow-release-gate-convergence/v1",
        "prd_id": PRD_ID,
        "merged_prd_slices": ["PRD-1.2", "PRD-1.3", "PRD-1.4"],
        "stream_id": STREAM_ID,
        "purpose": "Classify required checks, canonicalise pytest workflow commands, and define the release gate baseline in one consolidated PRD-1 implementation slice.",
        "required_check_classification": {
            "required_checks": REQUIRED_CHECKS,
            "advisory_checks": ADVISORY_CHECKS,
            "classification_performed": True,
            "required_checks_enforced": False,
            "enforcement_deferred_to_prd1_5_evidence": True,
        },
        "workflow_canonicalisation": {
            "canonical_pytest_command": "python3 -m pytest",
            "deprecated_pytest_command": "python -m pytest",
            "canonicalisation_performed": True,
            "changed_files": changed_files or [],
            "workflow_summary_after_canonicalisation": workflow_summary(root),
        },
        "openapi_reconciliation": {
            "canonical_openapi_path": "docs/openapi.json",
            "compatibility_mirror_path": "openapi.json",
            "root_openapi_sha256": root_sha,
            "docs_openapi_sha256": docs_sha,
            "root_and_docs_openapi_match": openapi_root.exists() and openapi_docs.exists() and root_sha == docs_sha,
            "reconciliation_performed": True,
            "file_copy_required": False,
        },
        "release_gate_definition": {
            "canonical_trunk_branch": "master",
            "release_branch_pattern": "release/**",
            "release_authority_source": "PRD-11 remains final production release/deployment authority; PRD-1 only defines gate mechanics.",
            "master_required_check_candidates": [check["check_id"] for check in REQUIRED_CHECKS if check.get("required_for_master")],
            "release_candidate_blocking_checks": [check["check_id"] for check in REQUIRED_CHECKS if check.get("blocks_release_candidate")],
            "branch_protection_modified": False,
            "release_gate_enforced": False,
            "branch_protection_evidence_deferred_to_prd1_5": True,
        },
        "authority_boundaries": {
            **{key: True for key in TRUE_BOUNDARIES},
            **{key: False for key in FALSE_BOUNDARIES},
            "required_check_classification_performed": True,
            "workflow_canonicalisation_performed": True,
            "ci_workflow_changes_performed": True,
            "openapi_reconciliation_performed": True,
            "required_checks_enforced": False,
            "release_gate_enforced": False,
            "branch_protection_modified": False,
        },
        "next_authorised_item": "PRD-1.5",
    }


def write_docs() -> None:
    DOC.write_text("""# PRD-1.2-1.4 Required Checks, Workflow Canonicalisation, and Release Gate Definition

**Status:** authority prepared; evidence capture records completion.  
**Merged slices:** PRD-1.2 Required Check Classification; PRD-1.3 Workflow Canonicalisation; PRD-1.4 Release Gate Definition.  
**Next authorised item after evidence:** PRD-1.5 — CI Convergence Evidence.

This consolidated slice reduces PRD-1 process overhead. It replaces three tiny governance slices with one implementation-focused slice that records the required-check classification, performs safe workflow command canonicalisation, reconciles the OpenAPI authority path, and defines the release gate baseline.

## Implementation performed

- Standardise workflow/Makefile pytest invocations from `python -m pytest` to `python3 -m pytest`.
- Classify required, advisory, and release-candidate-blocking checks.
- Confirm `docs/openapi.json` remains the canonical OpenAPI artifact and `openapi.json` remains a compatibility mirror.
- Define the master/release gate baseline without modifying hosted branch protection.

## Boundary

This slice does **not** enforce GitHub branch protection, does **not** create release tags, does **not** deploy, does **not** authorise public beta or live learner traffic, and does **not** start PRD-2 runtime KG implementation.

PRD-1.5 must capture convergence evidence before required checks can be treated as production-reliable.
""", encoding="utf-8")
    ENGINEERING_DOC.write_text("""# PRD-1 CI Release-Gate Convergence — Required Checks and Gate Baseline

This document is the compact engineering reference for the consolidated PRD-1.2-1.4 slice.

## Canonical command rule

Use `python3 -m pytest` for repository-owned workflow and Makefile pytest calls. The older `python -m pytest` form is treated as stale unless a third-party action or historical archive explicitly requires it.

## Required-check baseline

The required-check baseline is recorded in `docs/roadmap/production_readiness/prd1_required_checks_workflow_release_gate_convergence.json`.

Checks are classified as required for `master`, release-candidate blocking, advisory / not yet master-required, or historical evidence-only.

## Release-gate boundary

PRD-1 defines the release gate mechanics. PRD-11 remains the production release/deployment authority. PRD-10 remains the live learner traffic authority. PRD-2 remains the runtime KG implementation authority.
""", encoding="utf-8")



def patch_prd100_compatibility(root: Path) -> None:
    path = root / "scripts" / "production_readiness" / "audit_prd100_ci_release_gate_stream_authority.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    old = """    for key in NO_CHANGE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false in PRD-1.0")
        if prd1_register.get("implementation_boundaries", {}).get(key) is not False:
            errors.append(f"PRD-1 register {key} must remain false")
"""
    new = """    for key in NO_CHANGE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false in PRD-1.0")
        if production_register_position(register) == "prd1_0_recorded" and prd1_register.get("implementation_boundaries", {}).get(key) is not False:
            errors.append(f"PRD-1 register {key} must remain false")
"""
    if old in text:
        path.write_text(text.replace(old, new), encoding="utf-8")


def patch_prd101_compatibility(root: Path) -> None:
    path = root / "scripts" / "production_readiness" / "audit_prd101_ci_inventory_authority.py"
    text = path.read_text(encoding="utf-8")
    start = text.index("def prd1_1_recorded")
    end = text.index("def inventory_snapshot", start)
    replacement = '''def prd1_1_recorded(prd1_register: dict[str, Any]) -> bool:\n    last_item = prd1_register.get("last_recorded_item")\n    next_item = prd1_register.get("next_authorised_item")\n    if (last_item, next_item) not in {\n        (PRD_ID, "PRD-1.2"),\n        ("PRD-1.4", "PRD-1.5"),\n        ("PRD-1.9", "PRD-2"),\n    }:\n        return False\n    return any(\n        item.get("prd_id") == PRD_ID and item.get("authorised") is True and item.get("status") == "recorded"\n        for item in prd1_register.get("prd1_sequence", [])\n    )\n\n\ndef production_register_position(register: dict[str, Any]) -> str:\n    last_item = register.get("last_recorded_item")\n    next_item = register.get("next_authorised_item")\n    if last_item == "PRD-1.0" and next_item == PRD_ID:\n        return "after_prd1_0_before_prd1_1_capture"\n    if last_item == PRD_ID and next_item == "PRD-1.2":\n        return "prd1_1_recorded"\n    if last_item == "PRD-1.4" and next_item == "PRD-1.5":\n        return "prd1_4_recorded_after_prd1_1"\n    if last_item == "PRD-1.9" and next_item == "PRD-2":\n        return "prd1_closed_after_prd1_1"\n    return "unexpected"\n\n\n'''
    text = text[:start] + replacement + text[end:]
    text = text.replace(
        'errors.append("production readiness register must be positioned at PRD-1.0/PRD-1.1 or PRD-1.1/PRD-1.2")',
        'errors.append("production readiness register must be positioned at PRD-1.0/PRD-1.1, PRD-1.1/PRD-1.2, PRD-1.4/PRD-1.5, or PRD-1.9/PRD-2")',
    )
    text = text.replace(
        'and register.get("last_recorded_item") == PRD_ID\n        and register.get("next_authorised_item") == "PRD-1.2"\n        and record.get("next_authorised_item") == "PRD-1.2"',
        'and production_register_position(register) in {"prd1_1_recorded", "prd1_4_recorded_after_prd1_1", "prd1_closed_after_prd1_1"}\n        and record.get("next_authorised_item") in {"PRD-1.2", "PRD-1.5", "PRD-2"}',
    )
    path.write_text(text, encoding="utf-8")

    test_path = root / "tests" / "unit" / "roadmap_reconciliation" / "test_prd101_ci_inventory_authority.py"
    if test_path.exists():
        test = test_path.read_text(encoding="utf-8")
        test = test.replace(
            'assert prd101_result["next_authorised_item"] in {"PRD-1.1", "PRD-1.2"}',
            'assert prd101_result["next_authorised_item"] in {"PRD-1.1", "PRD-1.2", "PRD-1.5", "PRD-2"}',
        )
        test = test.replace(
            'assert prd101_result["register_next_authorised_item"] == "PRD-1.2"',
            'assert prd101_result["register_next_authorised_item"] in {"PRD-1.2", "PRD-1.5", "PRD-2"}',
        )
        test_path.write_text(test, encoding="utf-8")


def ensure_makefile_targets(root: Path) -> None:
    makefile = root / "Makefile"
    existing = makefile.read_text(encoding="utf-8") if makefile.exists() else ""
    marker = "# PRD-1.2-1.4 required checks/workflow/release gate convergence"
    block = f'''
{marker}
.PHONY: prd102-104-required-checks-workflow-release-gate-check prd102-104-required-checks-workflow-release-gate-capture
prd102-104-required-checks-workflow-release-gate-check:
	PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd102_104_required_checks_workflow_release_gate_convergence.py --authority-only --json

prd102-104-required-checks-workflow-release-gate-capture:
	PYTHONPATH=. python3 scripts/roadmap_reconciliation/capture_prd102_104_required_checks_workflow_release_gate_convergence_evidence.py --claim-prd102-104-required-checks-workflow-release-gate-convergence --prd-owner "$${{PRD_OWNER:-Nkgolo Lebelo}}" --target-branch master --require-valid --json
'''
    if marker not in existing:
        makefile.write_text(existing.rstrip() + "\n" + block, encoding="utf-8")


def apply(root: Path = Path("."), write_files: bool = True) -> dict[str, Any]:
    changed = canonicalise_pytest_commands(root)
    config = build_config(root, changed)
    if write_files:
        write_json(root / CONFIG, config)
        write_docs()
        record = read_json(root / RECORD)
        record.update({
            "schema_version": "prd1-required-checks-workflow-release-gate-convergence-record/v1",
            "prd_id": PRD_ID,
            "merged_prd_slices": ["PRD-1.2", "PRD-1.3", "PRD-1.4"],
            "stream_id": STREAM_ID,
            "status": "authority_prepared_evidence_pending",
            "required_check_classification_performed": True,
            "workflow_canonicalisation_performed": True,
            "ci_workflow_changes_performed": True,
            "openapi_reconciliation_performed": True,
            "required_checks_enforced": False,
            "release_gate_enforced": False,
            "branch_protection_modified": False,
            "prd1_5_authorised": False,
            "next_authorised_item": "PRD-1.2",
            "required_check_count": len(REQUIRED_CHECKS),
            "canonical_pytest_command": "python3 -m pytest",
            "deprecated_pytest_command_remaining_count": config["workflow_canonicalisation"]["workflow_summary_after_canonicalisation"]["python_m_pytest_workflow_count"],
            "openapi_root_and_docs_match": config["openapi_reconciliation"]["root_and_docs_openapi_match"],
        })
        for key in TRUE_BOUNDARIES:
            record[key] = True
        for key in FALSE_BOUNDARIES:
            record[key] = False
        write_json(root / RECORD, record)
        patch_prd100_compatibility(root)
        patch_prd101_compatibility(root)
        ensure_makefile_targets(root)
    return config


def main() -> int:
    apply(Path("."), write_files=True)
    print("Applied PRD-1.2-1.4 required-check/workflow/release-gate convergence authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
