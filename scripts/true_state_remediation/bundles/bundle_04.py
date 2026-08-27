"""EduBoost True-State Remediation — Bundle 04 (Architecture Debt & Schema Lifecycle Integrity).

This module implements the execution and verification harness for Bundle B04, covering:
- Slice TSR-6 (TSR-6.1 through TSR-6.17 -> RG-3A: Architecture and Service Boundaries)
- Slice TSR-7 (TSR-7.1 through TSR-7.13 -> RG-3B: Data Governance and Schema Lifecycle)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from scripts._subprocess import run
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

TASKS = [f"TSR-6.{i}" for i in range(1, 18)] + [f"TSR-7.{i}" for i in range(1, 14)]
MANUAL = (
    "TSR-6.1",
    "TSR-6.2",
    "TSR-6.3",
    "TSR-6.4",
    "TSR-6.10",
    "TSR-6.12",
    "TSR-6.14",
    "TSR-7.1",
    "TSR-7.2",
    "TSR-7.6",
    "TSR-7.8",
    "TSR-7.10",
    "TSR-7.12",
)


def prepare(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    env = environment_manifest(root)
    atomic_write_json(evidence_dir / "environment_manifest.json", env)
    previous = verify_previous_bundle(root, "B04")
    if not previous["valid"]:
        return {"valid": False, "error": f"Previous bundle B03 is not verified: {previous}"}
    return {"valid": True, "environment_manifest": str(evidence_dir / "environment_manifest.json")}


def apply(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    update_task_status(root, TASKS, "in_progress")
    update_bundle_status(root, "B04", "in_progress")

    # 1. Enforce Router/Repository Isolation
    ast_check = run_command(
        root,
        CommandSpec("check_router_repo_isolation", (sys.executable, "scripts/true_state_remediation/check_router_repo_isolation.py"), 120),
        evidence_dir / "apply",
    )
    if not ast_check["passed"]:
        return {"valid": False, "step": "check_router_repo_isolation", "result": ast_check}

    # 2. Enforce Legacy Quarantine & Router Contracts via Import Linter
    lint_bin = str(root / ".venv" / "bin" / "lint-imports") if (root / ".venv" / "bin" / "lint-imports").exists() else "lint-imports"
    lint_check = run_command(
        root,
        CommandSpec("lint_imports", (lint_bin,), 120),
        evidence_dir / "apply",
    )
    if not lint_check["passed"]:
        return {"valid": False, "step": "lint_imports", "result": lint_check}

    if skip_heavy:
        return {"valid": True, "structural_only": True}

    return {"valid": True}


def verify(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "register": verify_register(root),
        "boundaries": verify_false_release_boundaries(root),
    }

    # Check 1: Worktree hygiene (no stray or unrecognized untracked files)
    git = git_state(root)
    status_lines = [line.strip() for line in git.get("status_porcelain", "").splitlines() if line.strip()]
    stray_untracked = [
        line for line in status_lines 
        if line.startswith("??") and not (
            line.startswith("?? docs/release-evidence/") or 
            line.startswith("?? scripts/true_state_remediation/") or
            line.startswith("?? docs/architecture/") or
            line.startswith("?? docs/data/") or
            line.startswith("?? app/") or
            line.startswith("?? tests/integration/test_audit_immutability.py")
        )
    ]
    checks["hygiene"] = {
        "valid": git.get("available") is True and len(stray_untracked) == 0,
        "stray_untracked": stray_untracked,
        "status_porcelain": git.get("status_porcelain", ""),
    }

    # Check 2: Architecture Governance Artifacts (TSR-6)
    debt_reg = root / "docs/architecture/architectural_debt_register.json"
    cf_decomp = root / "docs/architecture/content_factory_capability_decomposition.md"
    etl_matrix = root / "docs/architecture/etl_consolidation_matrix.md"
    popia_bound = root / "docs/architecture/popia_orchestration_boundaries.md"
    auth_matrix = root / "docs/architecture/authorization_consolidation_matrix.md"
    legacy_bound = root / "docs/architecture/legacy_quarantine_boundary.md"
    complexity_budget = root / "docs/architecture/complexity_budgets_and_dispositions.md"
    
    arch_valid = all(p.exists() and p.stat().st_size > 100 for p in (
        debt_reg, cf_decomp, etl_matrix, popia_bound, auth_matrix, legacy_bound, complexity_budget
    ))
    checks["architecture_artifacts"] = {
        "valid": arch_valid,
        "debt_register": str(debt_reg),
        "content_factory_decomposition": str(cf_decomp),
        "etl_matrix": str(etl_matrix),
        "popia_boundaries": str(popia_bound),
        "authorization_matrix": str(auth_matrix),
        "legacy_quarantine": str(legacy_bound),
        "complexity_budgets": str(complexity_budget),
    }

    # Check 3: Data Governance Artifacts (TSR-7)
    data_inv = root / "docs/data/table_field_data_inventory.json"
    data_lineage = root / "docs/data/data_lineage_map.md"
    migration_policy = root / "docs/data/migration_rollback_and_forward_fix_policy.md"
    tx_policy = root / "docs/data/transaction_ownership_and_isolation_policy.md"
    audit_immutability_doc = root / "docs/data/audit_immutability_verification.md"
    backup_policy = root / "docs/data/backup_retention_and_erasure_policy.md"
    audit_immutability_test = root / "tests/integration/test_audit_immutability.py"

    data_valid = all(p.exists() and p.stat().st_size > 100 for p in (
        data_inv, data_lineage, migration_policy, tx_policy, audit_immutability_doc, backup_policy, audit_immutability_test
    ))
    checks["data_governance_artifacts"] = {
        "valid": data_valid,
        "data_inventory": str(data_inv),
        "data_lineage": str(data_lineage),
        "migration_policy": str(migration_policy),
        "transaction_policy": str(tx_policy),
        "audit_immutability_doc": str(audit_immutability_doc),
        "backup_policy": str(backup_policy),
        "audit_immutability_test": str(audit_immutability_test),
    }

    if skip_heavy:
        valid = all(c.get("valid") for c in checks.values())
        return {"valid": valid, "structural_only": True, "checks": checks}

    # Check 4: Check manual evidence records for architecture/data deliverables
    checks["manual"] = require_manual_evidence(root, "B04", MANUAL)

    valid = all(c.get("valid") for c in checks.values())
    if valid:
        update_task_status(root, TASKS, "verified", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B04", "verified", next_bundle_status="authorised")
    else:
        update_task_status(root, TASKS, "evidence_pending", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B04", "in_progress")

    atomic_write_json(evidence_dir / "verification.json", {"valid": valid, "checks": checks, "verified_at": utc_now()})
    return {"valid": valid, "checks": checks}
