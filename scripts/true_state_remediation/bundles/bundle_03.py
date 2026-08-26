"""EduBoost True-State Remediation — Bundle 03 (CI and Test Authority).

This module implements the execution and verification harness for Bundle B03, covering:
- Slice TSR-4 (TSR-4.1 through TSR-4.13 -> RG-2C: CI Authority and Governance Consolidation)
- Slice TSR-5 (TSR-5.1 through TSR-5.12 -> RG-2D: Test-System Taxonomy and Maintainability)
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
MANUAL = (
    "TSR-4.2", "TSR-4.6", "TSR-4.9", "TSR-4.10", "TSR-4.11", "TSR-4.12",
    "TSR-5.1", "TSR-5.4", "TSR-5.5", "TSR-5.7", "TSR-5.9", "TSR-5.10",
)


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
    
    # 1. Audit and generate CI workflow inventory (TSR-4.1, TSR-4.2, TSR-4.5, TSR-4.6, TSR-4.11)
    audit_ci = run_command(
        root,
        CommandSpec("audit_ci_workflows", (sys.executable, "scripts/maintenance/audit_ci_workflows.py"), 120),
        evidence_dir / "apply",
    )
    if not audit_ci["passed"]:
        return {"valid": False, "step": "audit_ci_workflows", "result": audit_ci}

    # 2. Record manual governance evidence (TSR-4.2, TSR-4.6, TSR-4.9..12, TSR-5.1, TSR-5.4, TSR-5.5, TSR-5.7, TSR-5.9, TSR-5.10)
    rec_manual = run_command(
        root,
        CommandSpec("record_manual_evidence", (sys.executable, "scripts/maintenance/record_b03_manual_evidence.py"), 120),
        evidence_dir / "apply",
    )
    if not rec_manual["passed"]:
        return {"valid": False, "step": "record_manual_evidence", "result": rec_manual}

    if skip_heavy:
        return {"valid": True, "structural_only": True}

    return {"valid": True}


def verify(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "register": verify_register(root),
        "boundaries": verify_false_release_boundaries(root),
    }

    # Check 1: CI workflow inventory document and JSON
    ci_doc = root / "docs/ci_workflow_inventory.md"
    ci_json = root / "docs/release-evidence/true-state-remediation/b03/ci/ci_workflow_inventory.json"
    checks["ci_inventory"] = {
        "valid": ci_doc.exists() and ci_doc.stat().st_size > 1000 and ci_json.exists() and ci_json.stat().st_size > 1000,
        "doc_path": str(ci_doc),
        "json_path": str(ci_json),
    }

    # Check 2: Pytest taxonomy configuration
    pytest_ini = root / "pytest.ini"
    checks["pytest_taxonomy"] = {
        "valid": pytest_ini.exists() and "unit:" in pytest_ini.read_text() and "governance:" in pytest_ini.read_text(),
        "path": str(pytest_ini),
    }

    if skip_heavy:
        valid = all(c.get("valid") for c in checks.values())
        return {"valid": valid, "structural_only": True, "checks": checks}

    # Check 3: Check manual evidence records for governance/architecture deliverables
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
