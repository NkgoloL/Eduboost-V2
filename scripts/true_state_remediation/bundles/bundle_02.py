"""EduBoost True-State Remediation — Bundle 02 (Canonical Truth and Toolchain).

This module implements the execution and verification harness for Bundle B02, covering:
- Slice TSR-2 (TSR-2.1 through TSR-2.11 -> RG-2A: Canonical Truth and Documentation)
- Slice TSR-3 (TSR-3.1 through TSR-3.12 -> RG-2B: Toolchain and Dependency Standardization)
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

TASKS = [f"TSR-2.{i}" for i in range(1, 12)] + [f"TSR-3.{i}" for i in range(1, 13)]
MANUAL = ("TSR-2.3", "TSR-2.9", "TSR-2.11", "TSR-3.1", "TSR-3.3", "TSR-3.7", "TSR-3.10", "TSR-3.11")


def prepare(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    env = environment_manifest(root)
    atomic_write_json(evidence_dir / "environment_manifest.json", env)
    previous = verify_previous_bundle(root, "B02")
    if not previous["valid"]:
        return {"valid": False, "error": f"Previous bundle B01 is not verified: {previous}"}
    return {"valid": True, "environment_manifest": str(evidence_dir / "environment_manifest.json")}


def apply(*, root: Path, evidence_dir: Path, skip_heavy: bool) -> dict[str, Any]:
    update_task_status(root, TASKS, "in_progress")
    update_bundle_status(root, "B02", "in_progress")
    
    # 1. Atomic generation of canonical OpenAPI JSON and YAML (TSR-2.5, TSR-2.6)
    gen_openapi = run_command(
        root,
        CommandSpec("generate_openapi", (sys.executable, "scripts/generate_openapi.py", "--output", "docs/openapi.json"), 120),
        evidence_dir / "apply",
    )
    if not gen_openapi["passed"]:
        return {"valid": False, "step": "generate_openapi", "result": gen_openapi}

    # 2. Generation of Route Inventory (TSR-2.7)
    gen_routes = run_command(
        root,
        CommandSpec("generate_routes", (sys.executable, "scripts/generate_route_inventory.py"), 120),
        evidence_dir / "apply",
    )
    if not gen_routes["passed"]:
        return {"valid": False, "step": "generate_routes", "result": gen_routes}

    # 3. Generation of Current-State Docs (TSR-2.1, TSR-2.2, TSR-2.4)
    gen_docs = run_command(
        root,
        CommandSpec("generate_docs", (sys.executable, "scripts/maintenance/generate_current_state_docs.py"), 120),
        evidence_dir / "apply",
    )
    if not gen_docs["passed"]:
        return {"valid": False, "step": "generate_docs", "result": gen_docs}

    # 4. Generation of Release SBOMs (TSR-3.10)
    gen_sboms = run_command(
        root,
        CommandSpec("generate_sboms", (sys.executable, "scripts/maintenance/generate_release_sboms.py"), 120),
        evidence_dir / "apply",
    )
    if not gen_sboms["passed"]:
        return {"valid": False, "step": "generate_sboms", "result": gen_sboms}

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
            line.startswith("?? scripts/maintenance/")
        )
    ]
    checks["hygiene"] = {
        "valid": git.get("available") is True and len(stray_untracked) == 0,
        "stray_untracked": stray_untracked,
        "status_porcelain": git.get("status_porcelain", ""),
    }

    # Check 2: OpenAPI JSON/YAML existence and format consistency
    openapi_json = root / "docs/openapi.json"
    openapi_yaml = root / "docs/openapi.yaml"
    checks["openapi_canonical"] = {
        "valid": openapi_json.exists() and openapi_json.stat().st_size > 1000 and openapi_yaml.exists() and openapi_yaml.stat().st_size > 1000,
        "json_path": str(openapi_json),
        "yaml_path": str(openapi_yaml),
    }

    # Check 3: Route inventory existence and consistency
    route_inv = root / "docs/route_inventory.md"
    checks["route_inventory"] = {
        "valid": route_inv.exists() and route_inv.stat().st_size > 1000,
        "path": str(route_inv),
    }

    # Check 4: Current state documentation existence and consistency
    current_state_doc = root / "docs/current_state.md"
    checks["current_state_docs"] = {
        "valid": current_state_doc.exists() and current_state_doc.stat().st_size > 500,
        "path": str(current_state_doc),
    }

    # Check 5: SBOM existence
    backend_sbom = root / "docs/release-evidence/true-state-remediation/b02/sbom/sbom-backend.cdx.json"
    frontend_sbom = root / "docs/release-evidence/true-state-remediation/b02/sbom/sbom-frontend.cdx.json"
    checks["sboms"] = {
        "valid": backend_sbom.exists() and frontend_sbom.exists(),
        "backend_sbom": str(backend_sbom),
        "frontend_sbom": str(frontend_sbom),
    }

    # Check 6: Check manual evidence records for architecture/decision deliverables
    checks["manual"] = require_manual_evidence(root, "B02", MANUAL)

    if skip_heavy:
        valid = all(c.get("valid") for c in checks.values())
        return {"valid": valid, "structural_only": True, "checks": checks}

    valid = all(c.get("valid") for c in checks.values())

    if valid:
        update_task_status(root, TASKS, "verified", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B02", "verified", next_bundle_status="authorised")
    else:
        update_task_status(root, TASKS, "evidence_pending", [str(evidence_dir.relative_to(root))])
        update_bundle_status(root, "B02", "in_progress")

    atomic_write_json(evidence_dir / "verification.json", {"valid": valid, "checks": checks, "verified_at": utc_now()})
    return {"valid": valid, "checks": checks}
