"""EduBoost True-State Remediation — Bundle 06 (Operations, Resiliency, and Billing Integrity).

This module implements the execution and verification harness for Bundle B06, covering:
- Slice TSR-10 (TSR-10.1 through TSR-10.8 -> RG-3D: Canonical API Routing & Deprecation)
- Slice TSR-11 (TSR-11.1 through TSR-11.16 -> RG-4: Operational Readiness, DR, and Billing Lock)
"""
from __future__ import annotations

import json
import os
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

TASKS = [f"TSR-10.{i}" for i in range(1, 9)] + [f"TSR-11.{i}" for i in range(1, 17)]
MANUAL = ("TSR-11.6", "TSR-11.16")


def prepare(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    env = environment_manifest(root)
    atomic_write_json(evidence_dir / "environment_manifest.json", env)
    previous = verify_previous_bundle(root, "B06")
    if not previous["valid"]:
        return {"valid": False, "error": f"Previous bundle B05 is not verified: {previous}"}
    return {"valid": True, "environment_manifest": str(evidence_dir / "environment_manifest.json")}


def apply(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    update_task_status(root, TASKS, "in_progress")
    update_bundle_status(root, "B06", "in_progress")

    # 1. Run Fast Automated Tests (Deprecation middleware, Billing Lock, Circuit Breaker, AI Budget)
    test_unit = run_command(
        root,
        CommandSpec(
            "test_b06_unit",
            (
                sys.executable,
                "-m",
                "pytest",
                "tests/unit/test_api_deprecation_middleware.py",
                "tests/integration/test_billing_lock_enforcement.py",
                "tests/unit/test_resilience_circuit_breaker.py",
                "tests/unit/test_ai_budget_guard.py",
                "-v",
            ),
            120,
            env={"EDUBOOST_REQUIRE_TEST_DB": "1", "AUTH_REFRESH_DB_PROOF_ENABLED": "1"},
        ),
        evidence_dir / "apply",
    )
    if not test_unit["passed"]:
        return {"valid": False, "step": "test_b06_unit", "result": test_unit}

    # 2. Run Disaster Recovery Dump-and-Restore Drill
    test_db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")
    test_dr = run_command(
        root,
        CommandSpec(
            "test_b06_dr_drill",
            (
                sys.executable,
                "-m",
                "pytest",
                "tests/integration/test_disaster_recovery_drill.py",
                "-v",
            ),
            180,
            env={
                "EDUBOOST_REQUIRE_TEST_DB": "1",
                "AUTH_REFRESH_DB_PROOF_ENABLED": "1",
                "DATABASE_URL": test_db_url,
            },
        ),
        evidence_dir / "apply",
    )
    if not test_dr["passed"]:
        return {"valid": False, "step": "test_b06_dr_drill", "result": test_dr}

    if skip_heavy:
        return {"valid": True, "structural_only": True}

    return {"valid": True}


def verify(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "register": verify_register(root),
        "boundaries": verify_false_release_boundaries(root),
    }

    # Check 1: Worktree hygiene (no stray untracked files)
    git = git_state(root)
    status_lines = [line.strip() for line in git.get("status_porcelain", "").splitlines() if line.strip()]
    stray_untracked = [
        line for line in status_lines
        if line.startswith("??") and not (
            line.startswith("?? docs/release-evidence/") or
            line.startswith("?? scripts/true_state_remediation/") or
            line.startswith("?? docs/operations/")
        )
    ]

    checks["hygiene"] = {
        "valid": git.get("available") is True and len(stray_untracked) == 0,
        "stray_untracked": stray_untracked,
        "status_porcelain": git.get("status_porcelain", ""),
    }

    # Check 2: Core Engineering Code Artifacts
    api_deprec = root / "app/middleware/api_deprecation.py"
    billing_guard = root / "app/services/billing_guard.py"
    ai_budget = root / "app/services/ai_budget_guard.py"
    test_deprec = root / "tests/unit/test_api_deprecation_middleware.py"
    test_billing = root / "tests/integration/test_billing_lock_enforcement.py"
    test_dr = root / "tests/integration/test_disaster_recovery_drill.py"
    test_circuit = root / "tests/unit/test_resilience_circuit_breaker.py"
    test_budget = root / "tests/unit/test_ai_budget_guard.py"

    code_valid = all(p.exists() and p.stat().st_size > 100 for p in (
        api_deprec, billing_guard, ai_budget, test_deprec, test_billing, test_dr, test_circuit, test_budget
    ))
    checks["engineering_proofs"] = {
        "valid": code_valid,
        "api_deprecation": str(api_deprec),
        "billing_guard": str(billing_guard),
        "ai_budget": str(ai_budget),
        "test_api_deprecation": str(test_deprec),
        "test_billing_lock": str(test_billing),
        "test_dr_drill": str(test_dr),
        "test_circuit_breaker": str(test_circuit),
        "test_ai_budget": str(test_budget),
    }

    # Check 3: Human Judgment Review Records (Lead Maintainer Exclusively)
    checks["manual"] = require_manual_evidence(root, "B06", MANUAL)

    if skip_heavy:
        valid = all(c.get("valid") for c in checks.values())
        return {"valid": valid, "structural_only": True, "checks": checks}

    valid = all(c.get("valid") for c in checks.values())
    if valid:
        update_task_status(root, TASKS, "verified", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B06", "verified", next_bundle_status="authorised")
    else:
        update_task_status(root, TASKS, "evidence_pending", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B06", "in_progress")

    atomic_write_json(evidence_dir / "verification.json", {"valid": valid, "checks": checks, "verified_at": utc_now()})
    return {"valid": valid, "checks": checks}
