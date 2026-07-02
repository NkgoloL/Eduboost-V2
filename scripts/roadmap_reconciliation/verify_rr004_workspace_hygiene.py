#!/usr/bin/env python3
"""Verify RR-004 workspace hygiene authority and evidence state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-004"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RECORD = Path("docs/roadmap/reconciliation/rr_004_workspace_hygiene_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_004_workspace_hygiene.md")
POLICY = Path("docs/operations/workspace_hygiene/rr004_workspace_hygiene_policy.md")
CLEANUP_POLICY = Path("docs/operations/workspace_hygiene/rr004_safe_cleanup_policy.md")
INVENTORY_DOC = Path("docs/operations/workspace_hygiene/rr004_tracked_file_audit_inventory.md")
SCANNER_DOC = Path("docs/operations/workspace_hygiene/rr004_reproducible_scanner_counts.md")
AUDIT_SCRIPT = Path("scripts/workspace_hygiene/audit_workspace_hygiene.py")
CLEANUP_SCRIPT = Path("scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr004_workspace_hygiene_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr004_workspace_hygiene.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_KEYS = (
    "workspace_hygiene_recorded",
    "safe_cleanup_target_recorded",
    "tracked_file_audit_inventory_recorded",
    "reproducible_scanner_counts_recorded",
    "ignored_artifact_cleanup_dry_run_only",
)


def _read(root: Path, path: Path) -> str:
    full = root / path
    return full.read_text(encoding="utf-8") if full.exists() else ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    register = _read(root, REGISTER)
    record = _json(root, RECORD)
    rr_doc = _read(root, RR_DOC)
    policy = _read(root, POLICY)
    cleanup_policy = _read(root, CLEANUP_POLICY)
    inventory_doc = _read(root, INVENTORY_DOC)
    scanner_doc = _read(root, SCANNER_DOC)
    audit_script = _read(root, AUDIT_SCRIPT)
    cleanup_script = _read(root, CLEANUP_SCRIPT)
    makefile = _read(root, MAKEFILE)

    checks = {
        "rr004_in_outstanding_register": RR_ID in register and "Workspace hygiene" in register,
        "rr_doc_exists": (root / RR_DOC).exists(),
        "record_exists": (root / RECORD).exists(),
        "policy_exists": (root / POLICY).exists(),
        "cleanup_policy_exists": (root / CLEANUP_POLICY).exists(),
        "inventory_doc_exists": (root / INVENTORY_DOC).exists(),
        "scanner_doc_exists": (root / SCANNER_DOC).exists(),
        "audit_script_exists": (root / AUDIT_SCRIPT).exists(),
        "cleanup_script_exists": (root / CLEANUP_SCRIPT).exists(),
        "rr_doc_cites_register_id": RR_ID in rr_doc,
        "policy_mentions_safe_cleanup": "Safe cleanup target" in policy and "dry-run" in policy,
        "cleanup_policy_is_dry_run_first": "git clean -ndX" in cleanup_policy and "--confirm-delete-ignored-artifacts" in cleanup_policy,
        "inventory_uses_tracked_files_only": "git ls-files" in inventory_doc and "tracked-file-only" in inventory_doc.lower(),
        "scanner_counts_are_reproducible": "reproducible scanner counts" in scanner_doc.lower() and "extension_counts" in scanner_doc,
        "audit_script_collects_tracked_counts": "git ls-files" in audit_script and "tracked_file_count" in audit_script,
        "cleanup_script_defaults_to_dry_run": "git clean" in cleanup_script and "-ndX" in cleanup_script,
        "makefile_has_dry_run_target": "rr004-ignored-artifact-clean-dry-run" in makefile,
        "makefile_has_audit_target": "rr004-workspace-hygiene-audit" in makefile,
        "capture_script_exists": (root / CAPTURE_SCRIPT).exists(),
        "verify_script_exists": (root / VERIFY_SCRIPT).exists(),
    }

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if record.get("__json_error__"):
        errors.append(f"record JSON invalid: {record['__json_error__']}")
    elif record:
        if record.get("rr_id") != RR_ID:
            errors.append(f"record rr_id must be {RR_ID}")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"boundary flag must remain false: {key}")
        if record.get("workspace_hygiene_recorded") is True:
            for key in REQUIRED_TRUE_KEYS:
                if record.get(key) is not True:
                    errors.append(f"record flag must be true after evidence capture: {key}")
            scanner_counts = record.get("scanner_counts") or {}
            if not isinstance(scanner_counts.get("tracked_file_count"), int):
                errors.append("scanner_counts.tracked_file_count must be an integer after capture")
        else:
            warnings.append("record is still pending evidence capture")
    else:
        errors.append("record JSON is missing")

    authority_errors = [
        err for err in errors
        if not err.startswith("record flag must be true") and "scanner_counts.tracked_file_count" not in err
    ]
    authority_valid = not authority_errors
    valid = not errors and record.get("workspace_hygiene_recorded") is True

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "workspace_hygiene_recorded": record.get("workspace_hygiene_recorded") is True,
        "safe_cleanup_target_recorded": record.get("safe_cleanup_target_recorded") is True,
        "tracked_file_audit_inventory_recorded": record.get("tracked_file_audit_inventory_recorded") is True,
        "reproducible_scanner_counts_recorded": record.get("reproducible_scanner_counts_recorded") is True,
        "ignored_artifact_cleanup_dry_run_only": record.get("ignored_artifact_cleanup_dry_run_only") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed") is True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    parser.add_argument("--authority-only", action="store_true", help="exit successfully when authority files are installed even if evidence is pending")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("RR-004 workspace hygiene verification")
        print(f"valid: {result['valid']}")
        print(f"authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if args.authority_only:
        return 0 if result["authority_valid"] else 1
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
