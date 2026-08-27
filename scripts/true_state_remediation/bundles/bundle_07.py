"""EduBoost True-State Remediation — Bundle 07 (Final Release Gate, Stabilization, and Production Baseline Verification).

This module implements the execution and verification harness for Bundle B07, covering:
- Slice TSR-12 (TSR-12.1 through TSR-12.10 -> RG-5: Production Pilot Authorization & Controlled Deployment Gates)
- Slice TSR-13 (TSR-13.1 through TSR-13.9 -> RG-6: Post-Release Stabilization, Debt Ratchets & Baseline Authority)
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
from scripts.true_state_remediation.verify_final_program import (
    verify_engineering_proofs,
)

TASKS = [f"TSR-12.{i}" for i in range(1, 11)] + [f"TSR-13.{i}" for i in range(1, 10)]
MANUAL = ("TSR-12.3", "TSR-12.4", "TSR-12.7", "TSR-12.8")


def prepare(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    env = environment_manifest(root)
    atomic_write_json(evidence_dir / "environment_manifest.json", env)
    previous = verify_previous_bundle(root, "B07")
    if not previous["valid"]:
        return {"valid": False, "error": f"Previous bundle B06 is not verified: {previous}"}
    return {"valid": True, "environment_manifest": str(evidence_dir / "environment_manifest.json")}


def apply(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    update_task_status(root, TASKS, "in_progress")
    update_bundle_status(root, "B07", "in_progress")

    py_exec = str(root / ".venv/bin/python") if (root / ".venv/bin/python").exists() else sys.executable

    # 1. Generate Authoritative Release Statement
    gen_stmt = run_command(
        root,
        CommandSpec(
            "generate_release_statement",
            (
                py_exec,
                "scripts/maintenance/generate_release_statement.py",
            ),
            60,
        ),
        evidence_dir / "apply",
    )
    if not gen_stmt["passed"]:
        return {"valid": False, "step": "generate_release_statement", "result": gen_stmt}

    # 2. Run Fast Automated Final Verification Tests
    test_final = run_command(
        root,
        CommandSpec(
            "test_b07_final_program",
            (
                py_exec,
                "-m",
                "pytest",
                "tests/unit/test_true_state_final_program.py",
                "-v",
            ),
            120,
        ),
        evidence_dir / "apply",
    )
    if not test_final["passed"]:
        return {"valid": False, "step": "test_b07_final_program", "result": test_final}

    if skip_heavy:
        return {"valid": True, "structural_only": True}

    return {"valid": True}


def verify(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "register": verify_register(root),
        "boundaries": verify_false_release_boundaries(root),
    }

    # Check 1: Worktree hygiene (no stray untracked files outside declared scopes)
    git = git_state(root)
    status_lines = [line.strip() for line in git.get("status_porcelain", "").splitlines() if line.strip()]
    stray_untracked = [
        line for line in status_lines
        if line.startswith("??") and not (
            line.startswith("?? docs/release-evidence/") or
            line.startswith("?? scripts/true_state_remediation/") or
            line.startswith("?? docs/releases/") or
            line.startswith("?? docs/release/") or
            line.startswith("?? docs/operations/") or
            line.startswith("?? docs/architecture/") or
            line.startswith("?? docs/curriculum/") or
            line.startswith("?? docs/infrastructure/") or
            line.startswith("?? docs/roadmap/") or
            line.startswith("?? scripts/maintenance/") or
            line.startswith("?? app/") or
            line.startswith("?? tests/")
        )
    ]
    checks["hygiene"] = {
        "valid": git.get("available") is True and len(stray_untracked) == 0,
        "stray_untracked": stray_untracked,
        "status_porcelain": git.get("status_porcelain", ""),
    }

    # Check 2: Core Engineering Code & Delivery Artifacts
    checks["engineering_proofs"] = verify_engineering_proofs(root)

    # Check 3: Human Judgment Review Records (Lead Maintainer Exclusively)
    checks["manual"] = require_manual_evidence(root, "B07", MANUAL)

    if skip_heavy:
        valid = all(c.get("valid") for c in checks.values())
        return {"valid": valid, "structural_only": True, "checks": checks}

    valid = all(c.get("valid") for c in checks.values())
    if valid:
        update_task_status(root, TASKS, "verified", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B07", "verified")
    else:
        update_task_status(root, TASKS, "evidence_pending", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B07", "in_progress")

    atomic_write_json(evidence_dir / "verification.json", {"valid": valid, "checks": checks, "verified_at": utc_now()})
    return {"valid": valid, "checks": checks}
