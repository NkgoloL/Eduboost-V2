"""EduBoost True-State Remediation — Bundle 03 (CI Authority and Test-System Taxonomy Consolidation).

This module implements the execution and verification harness for Bundle B03, covering:
- Slice TSR-4 (TSR-4.1 through TSR-4.13 -> RG-2 CI Authority and Governance Consolidation)
- Slice TSR-5 (TSR-5.1 through TSR-5.12 -> RG-2 Test-System Taxonomy, Isolation, and Health)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from scripts.true_state_remediation.core import (
    BundleError,
    CommandSpec,
    atomic_write_json,
    environment_manifest,
    git_state,
    load_json,
    require_manual_evidence,
    run_command,
    update_bundle_status,
    update_task_status,
    utc_now,
    verify_false_release_boundaries,
    verify_previous_bundle,
    verify_register,
)

TASKS = [f"TSR-4.{i}" for i in range(1, 14)] + [f"TSR-5.{i}" for i in range(1, 13)]
MANUAL = ("TSR-4.2", "TSR-4.9", "TSR-4.10", "TSR-5.5", "TSR-5.9")

CANONICAL_WORKFLOW_FILES = {
    "pr-core.yml",
    "product-runtime.yml",
    "frontend-e2e.yml",
    "security-supply-chain.yml",
    "release-evidence.yml",
    "operations-drills.yml",
}


def prepare(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    env = environment_manifest(root)
    atomic_write_json(evidence_dir / "environment_manifest.json", env)
    previous = verify_previous_bundle(root, "B03")
    if not previous["valid"]:
        return {"valid": False, "error": f"Previous bundle B02 is not verified: {previous}"}
    return {"valid": True, "environment_manifest": str(evidence_dir / "environment_manifest.json")}


def apply(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    update_task_status(root, TASKS, "in_progress")
    update_bundle_status(root, "B03", "in_progress")

    # 1. Generate CI Authority Matrix & Workflow Inventory (TSR-4.1, TSR-4.2, TSR-4.11)
    gen_ci = run_command(
        root,
        CommandSpec("generate_ci_authority", (sys.executable, "scripts/maintenance/generate_ci_authority_inventory.py"), 120),
        evidence_dir / "apply",
    )
    if not gen_ci["passed"]:
        return {"valid": False, "step": "generate_ci_authority", "result": gen_ci}

    # 2. Generate Test Health Metrics (TSR-5.12)
    gen_metrics = run_command(
        root,
        CommandSpec("generate_test_health_metrics", (sys.executable, "scripts/maintenance/generate_test_health_metrics.py"), 120),
        evidence_dir / "apply",
    )
    if not gen_metrics["passed"]:
        return {"valid": False, "step": "generate_test_health_metrics", "result": gen_metrics}

    # 3. Generate Current-State Documentation (TSR-4.12, TSR-5.3)
    gen_docs = run_command(
        root,
        CommandSpec("generate_current_state", (sys.executable, "scripts/maintenance/generate_current_state_docs.py"), 120),
        evidence_dir / "apply",
    )
    if not gen_docs["passed"]:
        return {"valid": False, "step": "generate_current_state", "result": gen_docs}

    if skip_heavy:
        return {"valid": True, "structural_only": True}

    return {"valid": True}


def verify(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "register": verify_register(root),
        "boundaries": verify_false_release_boundaries(root),
    }

    # Check 1: Worktree hygiene & strict diff-stat (no stray untracked outside allowed prefixes)
    git = git_state(root)
    status_lines = [line.strip() for line in git.get("status_porcelain", "").splitlines() if line.strip()]
    stray_untracked = [
        line for line in status_lines 
        if line.startswith("??") and not (
            line.startswith("?? docs/release-evidence/") or 
            line.startswith("?? scripts/true_state_remediation/") or
            line.startswith("?? scripts/maintenance/") or
            line.startswith("?? config/true_state_remediation/") or
            line.startswith("?? docs/ci/") or
            line.startswith("?? docs/testing/") or
            line.startswith("?? archive/github_workflows/") or
            line.startswith("?? tests/taxonomy.py")
        )
    ]
    checks["hygiene"] = {
        "valid": git.get("available") is True and len(stray_untracked) == 0,
        "stray_untracked": stray_untracked,
        "status_porcelain": git.get("status_porcelain", ""),
    }

    # Check 2: Active workflows directory contains ONLY the canonical 6 workflows
    active_wf_files = {p.name for p in (root / ".github/workflows").glob("*.yml")}
    wf_valid = (active_wf_files == CANONICAL_WORKFLOW_FILES)
    checks["canonical_workflows"] = {
        "valid": wf_valid,
        "active_workflows": sorted(list(active_wf_files)),
        "expected_canonical": sorted(list(CANONICAL_WORKFLOW_FILES)),
        "unexpected": sorted(list(active_wf_files - CANONICAL_WORKFLOW_FILES)),
        "missing": sorted(list(CANONICAL_WORKFLOW_FILES - active_wf_files)),
    }

    # Check 3: CI authority matrix and inventory existence
    matrix_file = root / "docs/ci/ci_authority_matrix.json"
    inv_file = root / "docs/ci/ci_workflow_inventory.md"
    checks["ci_authority_matrix"] = {
        "valid": matrix_file.exists() and inv_file.exists() and matrix_file.stat().st_size > 1000,
        "matrix_path": str(matrix_file),
        "inventory_path": str(inv_file),
    }

    # Check 4: Test taxonomy and fast-suite manifest
    tax_doc = root / "docs/testing/test_taxonomy_and_fast_suite_manifest.md"
    tax_module = root / "tests/taxonomy.py"
    checks["test_taxonomy"] = {
        "valid": tax_doc.exists() and tax_module.exists(),
        "doc_path": str(tax_doc),
        "module_path": str(tax_module),
    }

    # Check 5: Flake policy and quarantine register
    flake_doc = root / "docs/testing/flake_policy_and_quarantine_register.md"
    checks["flake_policy"] = {
        "valid": flake_doc.exists() and flake_doc.stat().st_size > 200,
        "path": str(flake_doc),
    }

    # Check 6: Risk-based coverage thresholds
    cov_doc = root / "docs/testing/risk_based_coverage_thresholds.md"
    checks["risk_coverage_thresholds"] = {
        "valid": cov_doc.exists() and cov_doc.stat().st_size > 200,
        "path": str(cov_doc),
    }

    # Check 7: Test health metrics
    metrics_file = root / "docs/testing/test_health_metrics.json"
    checks["test_health_metrics"] = {
        "valid": metrics_file.exists() and metrics_file.stat().st_size > 100,
        "path": str(metrics_file),
    }

    if skip_heavy:
        valid = all(c.get("valid") for c in checks.values())
        return {"valid": valid, "structural_only": True, "checks": checks}

    # Check 8: Check manual evidence records via single-source verification
    checks["manual"] = require_manual_evidence(root, "B03", MANUAL)

    valid = all(c.get("valid") for c in checks.values())
    if valid:
        update_task_status(root, TASKS, "verified", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B03", "verified", next_bundle_status="authorised")
    else:
        update_task_status(root, TASKS, "evidence_pending", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B03", "in_progress")

    atomic_write_json(evidence_dir / "verification.json", {"valid": valid, "checks": checks, "verified_at": utc_now()})
    return {"valid": valid, "checks": checks}
