#!/usr/bin/env python3
"""Audit RR-009 governance/process reconciliation documents."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT_ADR_DIR = Path("docs/adr")
FRONTEND_ADR_DIR = Path("docs/adr/frontend")
ADR_README = Path("docs/adr/README.md")
CURRENT_STATE = Path("docs/current_state.md")
EXTERNAL_TODO = Path("docs/governance/rr009_external_todo_ownership_register.md")
BRANCH_PROTECTION_DOC = Path("docs/release/current/branch_protection_evidence.md")
RELEASE_README = Path("docs/release/current/README.md")
MANIFEST = Path("docs/governance/rr009_governance_process_manifest.json")

EXCLUDED_ADR_FILES = {"README.md", "TEMPLATE.md", "sign-off.md"}


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


def _adr_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for directory in (ROOT_ADR_DIR, FRONTEND_ADR_DIR):
        full_dir = root / directory
        if not full_dir.exists():
            continue
        for path in sorted(full_dir.glob("*.md")):
            if path.name in EXCLUDED_ADR_FILES:
                continue
            files.append(path.relative_to(root / ROOT_ADR_DIR))
    return files


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    current_state = _read(root, CURRENT_STATE)
    adr_readme = _read(root, ADR_README)
    external_todo = _read(root, EXTERNAL_TODO)
    branch_doc = _read(root, BRANCH_PROTECTION_DOC)
    release_readme = _read(root, RELEASE_README)
    manifest = _json(root, MANIFEST)

    adr_files = _adr_files(root)
    missing_adr_index_entries = [str(path) for path in adr_files if str(path) not in adr_readme and path.name not in adr_readme]

    checks = {
        "current_state_exists": (root / CURRENT_STATE).exists(),
        "current_state_reviewed_2026_07_02": "last_reviewed: 2026-07-02" in current_state,
        "current_state_refresh_marker_present": "Current-state refresh cadence recorded: true" in current_state,
        "current_state_mentions_rr_register_rule": "RR-###" in current_state and "outstanding_work_register.md" in current_state,
        "adr_readme_exists": (root / ADR_README).exists(),
        "adr_index_completion_marker_present": "ADR index completion recorded: true" in adr_readme,
        "all_adr_files_indexed": not missing_adr_index_entries,
        "external_todo_register_exists": (root / EXTERNAL_TODO).exists(),
        "external_todo_marker_present": "External TODO ownership recorded: true" in external_todo,
        "external_todo_has_owners_and_dates": "Owner" in external_todo and "Target review date" in external_todo and "RR-015" in external_todo,
        "branch_protection_doc_exists": (root / BRANCH_PROTECTION_DOC).exists(),
        "branch_protection_marker_present": "Branch protection reflected in canonical release docs: true" in branch_doc,
        "release_readme_links_branch_doc": "branch_protection_evidence.md" in release_readme,
        "manifest_exists": (root / MANIFEST).exists(),
        "rr003_caveat_visible": "RR-003" in current_state and "0.0" in current_state,
        "rr006_caveat_visible": "RR-006" in current_state and "non-required" in current_state,
        "rr010_remaining_visible": "RR-010" in current_state and "outstanding" in current_state.lower(),
        "rr015_remaining_visible": "RR-015" in external_todo and "outstanding" in external_todo.lower(),
        "rr016_remaining_visible": "RR-016" in current_state and "outstanding" in current_state.lower(),
    }

    errors = [f"missing or failed check: {key}" for key, passed in checks.items() if not passed]
    if manifest.get("__json_error__"):
        errors.append(f"manifest JSON invalid: {manifest['__json_error__']}")
    elif manifest:
        for key in (
            "current_state_refresh_cadence_recorded",
            "adr_index_completed",
            "external_todo_ownership_recorded",
            "branch_protection_release_docs_recorded",
            "rr003_fallback_coverage_caveat_visible",
            "rr006_non_required_checks_caveat_visible",
            "rr010_beta_outcome_reporting_remaining_visible",
            "rr015_external_approvals_remaining_visible",
            "rr016_operational_drills_remaining_visible",
        ):
            if manifest.get(key) is not True:
                errors.append(f"manifest flag must be true: {key}")
        for key in (
            "production_release_authorised",
            "deployment_authorised",
            "release_tag_authorised",
            "public_beta_authorised",
            "runtime_kg_implementation_claimed",
        ):
            if manifest.get(key) is not False:
                errors.append(f"manifest boundary flag must be false: {key}")
    else:
        errors.append("manifest is missing")

    return {
        "valid": not errors,
        "checks": checks,
        "errors": errors,
        "adr_files_indexed_count": len(adr_files) - len(missing_adr_index_entries),
        "adr_files_total": len(adr_files),
        "missing_adr_index_entries": missing_adr_index_entries,
        "current_state_refresh_cadence_recorded": checks["current_state_refresh_marker_present"],
        "adr_index_completed": checks["all_adr_files_indexed"] and checks["adr_index_completion_marker_present"],
        "external_todo_ownership_recorded": checks["external_todo_marker_present"],
        "branch_protection_release_docs_recorded": checks["branch_protection_marker_present"] and checks["release_readme_links_branch_doc"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
