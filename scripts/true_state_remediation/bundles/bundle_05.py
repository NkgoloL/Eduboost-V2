"""EduBoost True-State Remediation — Bundle 05 (Security, Privacy, and Educational Validity).

This module implements the execution and verification harness for Bundle B05, covering:
- Slice TSR-8 (TSR-8.1 through TSR-8.17 -> RG-3A: Security Architecture and Privacy Enforcement)
- Slice TSR-9 (TSR-9.1 through TSR-9.14 -> RG-3C: Educational Validity and Mastery Modeling)
"""
from __future__ import annotations

import json
import os
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

TASKS = [f"TSR-8.{i}" for i in range(1, 18)] + [f"TSR-9.{i}" for i in range(1, 15)]
MANUAL = ("TSR-8.1", "TSR-9.1")


def prepare(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    env = environment_manifest(root)
    atomic_write_json(evidence_dir / "environment_manifest.json", env)
    previous = verify_previous_bundle(root, "B05")
    if not previous["valid"]:
        return {"valid": False, "error": f"Previous bundle B04 is not verified: {previous}"}
    return {"valid": True, "environment_manifest": str(evidence_dir / "environment_manifest.json")}


def apply(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    update_task_status(root, TASKS, "in_progress")
    update_bundle_status(root, "B05", "in_progress")

    # 1. Run Unit Tests (PII sanitization, mastery bounds, object isolation)
    test_unit = run_command(
        root,
        CommandSpec(
            "test_b05_unit",
            (
                sys.executable,
                "-m",
                "pytest",
                "tests/unit/test_pii_sanitization.py",
                "tests/unit/test_mastery_semantics.py",
                "tests/unit/test_security_object_isolation.py",
                "-v",
            ),
            120,
        ),
        evidence_dir / "apply",
    )
    if not test_unit["passed"]:
        return {"valid": False, "step": "test_b05_unit", "result": test_unit}

    # 2. Run Integration Tests (POPIA DSR cascade, Curriculum Graph migration)
    test_db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")
    test_integration = run_command(
        root,
        CommandSpec(
            "test_b05_integration",
            (
                sys.executable,
                "-m",
                "pytest",
                "tests/integration/test_popia_dsr_automation.py",
                "tests/integration/test_curriculum_graph_migration.py",
                "-v",
            ),
            180,
            env={"AUTH_REFRESH_DB_PROOF_ENABLED": "1", "DATABASE_URL": test_db_url},
        ),
        evidence_dir / "apply",
    )
    if not test_integration["passed"]:
        return {"valid": False, "step": "test_b05_integration", "result": test_integration}

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
            line.startswith("?? docs/privacy/") or
            line.startswith("?? docs/curriculum/") or
            line.startswith("?? app/") or
            line.startswith("?? tests/")
        )
    ]
    checks["hygiene"] = {
        "valid": git.get("available") is True and len(stray_untracked) == 0,
        "stray_untracked": stray_untracked,
        "status_porcelain": git.get("status_porcelain", ""),
    }

    # Check 2: Core Engineering Code Artifacts
    pii_sanitizer = root / "app/core/pii_sanitizer.py"
    mastery_engine = root / "app/services/mastery_engine.py"
    dsr_service = root / "app/services/popia_dsr_service.py"
    test_pii = root / "tests/unit/test_pii_sanitization.py"
    test_mastery = root / "tests/unit/test_mastery_semantics.py"
    test_isolation = root / "tests/unit/test_security_object_isolation.py"
    test_dsr = root / "tests/integration/test_popia_dsr_automation.py"
    test_graph = root / "tests/integration/test_curriculum_graph_migration.py"

    code_valid = all(p.exists() and p.stat().st_size > 100 for p in (
        pii_sanitizer, mastery_engine, dsr_service, test_pii, test_mastery, test_isolation, test_dsr, test_graph
    ))
    checks["engineering_proofs"] = {
        "valid": code_valid,
        "pii_sanitizer": str(pii_sanitizer),
        "mastery_engine": str(mastery_engine),
        "dsr_service": str(dsr_service),
        "test_pii": str(test_pii),
        "test_mastery": str(test_mastery),
        "test_isolation": str(test_isolation),
        "test_dsr": str(test_dsr),
        "test_graph": str(test_graph),
    }

    # Check 3: Human Judgment Review Records
    checks["manual"] = require_manual_evidence(root, "B05", MANUAL)

    if skip_heavy:
        valid = all(c.get("valid") for c in checks.values())
        return {"valid": valid, "structural_only": True, "checks": checks}

    valid = all(c.get("valid") for c in checks.values())
    if valid:
        update_task_status(root, TASKS, "verified", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B05", "verified", next_bundle_status="authorised")
    else:
        update_task_status(root, TASKS, "evidence_pending", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B05", "in_progress")

    atomic_write_json(evidence_dir / "verification.json", {"valid": valid, "checks": checks, "verified_at": utc_now()})
    return {"valid": valid, "checks": checks}
