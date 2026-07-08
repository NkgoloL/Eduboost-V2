#!/usr/bin/env python3
"""Audit PRD-0.9 repository hygiene and generated/local artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd008_branch_release_naming_reconciliation import evaluate as evaluate_prd008

PRD_ID = "PRD-0.9"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_009_repository_hygiene_generated_local_artifact_audit.md"
PLAN = ROOT / "repository_hygiene_generated_local_artifact_audit_plan.md"
SCHEMA_DOC = ROOT / "repository_hygiene_generated_local_artifact_audit.schema.md"
RECORD = ROOT / "prd_009_repository_hygiene_generated_local_artifact_audit_record.json"
INVENTORY = ROOT / "repository_hygiene_generated_local_artifact_audit.json"
POLICY_DOC = Path("docs/engineering/repository_hygiene.md")

TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]
CLEANUP_FALSE_KEYS = ["generated_local_cleanup_authorised", "file_deletion_authorised", "artifact_deletion_authorised", "repository_history_rewrite_authorised"]

GENERATED_LOCAL_CANDIDATES: list[dict[str, str]] = [
    {"path": "coverage.xml", "class": "coverage_report", "policy": "regenerate_not_source_authority"},
    {"path": "htmlcov", "class": "coverage_report", "policy": "local_output"},
    {"path": ".coverage", "class": "coverage_report", "policy": "local_output"},
    {"path": ".pytest_cache", "class": "test_cache", "policy": "local_output"},
    {"path": ".mypy_cache", "class": "typecheck_cache", "policy": "local_output"},
    {"path": ".ruff_cache", "class": "lint_cache", "policy": "local_output"},
    {"path": ".hypothesis", "class": "test_cache", "policy": "local_output"},
    {"path": "playwright-report", "class": "browser_test_report", "policy": "local_output"},
    {"path": "test-results", "class": "browser_test_output", "policy": "local_output"},
    {"path": "logs", "class": "runtime_logs", "policy": "local_output_or_evidence_candidate"},
    {"path": "temp", "class": "temporary_files", "policy": "local_output"},
    {"path": ".tmp", "class": "temporary_files", "policy": "local_output"},
    {"path": "scratch", "class": "temporary_files", "policy": "local_output"},
    {"path": "var", "class": "runtime_state", "policy": "local_output"},
    {"path": "eduboost.egg-info", "class": "package_metadata", "policy": "generated_build_metadata"},
    {"path": "app/frontend/out", "class": "frontend_build_output", "policy": "generated_build_output"},
    {"path": "app/frontend/coverage", "class": "frontend_coverage", "policy": "local_output"},
    {"path": "data/exports", "class": "data_export", "policy": "local_output"},
    {"path": "data/temp", "class": "temporary_data", "policy": "local_output"},
    {"path": "data/synthetic", "class": "synthetic_data_output", "policy": "local_output"},
    {"path": "artifacts/llm", "class": "llm_artifact_output", "policy": "local_output"},
    {"path": "docs/api/_build", "class": "docs_build_output", "policy": "generated_build_output"},
    {"path": "bicep/container_apps.json", "class": "generated_infra_json", "policy": "generated_from_bicep_source"},
    {"path": "backups-local-test", "class": "local_backup", "policy": "local_backup"},
    {"path": "backups-matrix-test", "class": "local_backup", "policy": "local_backup"},
]

SUSPICIOUS_TOP_LEVEL_EXACT = {
    "cripts": "pager/help output captured as a top-level file",
    "tatus": "branch/status command output captured as a top-level file",
    "ubprocess, sys": "patch/diff or command-output fragment captured as a top-level file",
}
SUSPICIOUS_TOP_LEVEL_PREFIXES = {
    "coped technical delivery directories": "branch/status command output captured with a truncated filename",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def count_files_and_bytes(path: Path, limit: int = 5000) -> tuple[int, int, bool]:
    if not path.exists():
        return 0, 0, False
    if path.is_file():
        try:
            return 1, path.stat().st_size, False
        except OSError:
            return 1, 0, False
    files = 0
    total = 0
    truncated = False
    for child in path.rglob("*"):
        if child.is_file():
            files += 1
            try:
                total += child.stat().st_size
            except OSError:
                pass
            if files >= limit:
                truncated = True
                break
    return files, total, truncated


def ignored_by_policy(rel_path: str, ignore_text: str) -> bool:
    rel = rel_path.strip("/")
    options = {rel, f"{rel}/", f"/{rel}", f"/{rel}/"}
    if rel.startswith("artifacts/"):
        options.add("artifacts/llm/")
    if rel.startswith("app/frontend/out"):
        options.add("app/frontend/out/")
    if rel.startswith("app/frontend/coverage"):
        options.add("app/frontend/coverage/")
    if rel.startswith("data/"):
        options.add(rel + "/")
    lines = {line.strip() for line in ignore_text.splitlines() if line.strip() and not line.strip().startswith("#")}
    return any(option in lines for option in options)


def terminal_artifact_markers(path: Path) -> list[str]:
    markers: list[str] = []
    if not path.is_file():
        return markers
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return markers
    if b"\x1b[" in sample:
        markers.append("ansi_escape_sequence")
    if b"\x08" in sample:
        markers.append("backspace_overstrike_sequence")
    if b"Merge pull request" in sample or b"branch" in sample[:512].lower():
        markers.append("branch_or_git_output")
    return markers


def generated_local_candidates(root: Path) -> list[dict[str, Any]]:
    ignore_text = read_text(root / ".gitignore")
    items: list[dict[str, Any]] = []
    for candidate in GENERATED_LOCAL_CANDIDATES:
        rel_path = candidate["path"]
        path = root / rel_path
        file_count, total_bytes, truncated = count_files_and_bytes(path)
        exists = path.exists()
        ignored = ignored_by_policy(rel_path, ignore_text)
        items.append({
            "path": rel_path,
            "artifact_class": candidate["class"],
            "policy": candidate["policy"],
            "exists": exists,
            "is_file": path.is_file() if exists else False,
            "is_dir": path.is_dir() if exists else False,
            "file_count": file_count,
            "total_bytes_estimate": total_bytes,
            "count_truncated": truncated,
            "ignored_by_policy": ignored,
            "disposition": "inventory_only_no_cleanup_authorised",
        })
    return items


def suspicious_top_level_entries(root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name) if root.exists() else []:
        name = path.name
        reasons: list[str] = []
        if name in SUSPICIOUS_TOP_LEVEL_EXACT:
            reasons.append(SUSPICIOUS_TOP_LEVEL_EXACT[name])
        for prefix, reason in SUSPICIOUS_TOP_LEVEL_PREFIXES.items():
            if name.startswith(prefix):
                reasons.append(reason)
        if path.is_file():
            reasons.extend(terminal_artifact_markers(path))
        if reasons:
            try:
                size = path.stat().st_size
            except OSError:
                size = 0
            items.append({
                "path": name,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size_bytes": size,
                "reasons": sorted(set(reasons)),
                "disposition": "inventory_only_no_cleanup_authorised",
            })
    return items


def repository_hygiene_inventory(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    candidates = generated_local_candidates(root)
    suspicious = suspicious_top_level_entries(root)
    policy_text = read_text(root / POLICY_DOC)
    policy_ok = "PRD-0.9" in policy_text and "does not delete files" in policy_text and "PRD-1 implementation" in policy_text
    present = [item for item in candidates if item["exists"]]
    ignored_present = [item for item in present if item["ignored_by_policy"]]
    unignored_present = [item for item in present if not item["ignored_by_policy"]]
    terminal_count = sum(1 for item in suspicious if any("sequence" in reason or "output" in reason for reason in item["reasons"]))
    total_bytes = sum(int(item.get("total_bytes_estimate") or 0) for item in candidates)
    try:
        top_level_count = len(list(root.iterdir()))
    except OSError:
        top_level_count = 0
    return {
        "schema_version": "prd-repository-hygiene-generated-local-artifact-audit/v1",
        "prd_id": PRD_ID,
        "captured_at": captured_at,
        "repository_hygiene_policy_document": str(POLICY_DOC),
        "repository_hygiene_policy_document_refreshed": policy_ok,
        "generated_local_artifact_candidates": candidates,
        "suspicious_top_level_entries": suspicious,
        "summary": {
            "top_level_entry_count": top_level_count,
            "configured_generated_local_path_count": len(candidates),
            "present_generated_local_path_count": len(present),
            "ignored_present_generated_local_path_count": len(ignored_present),
            "unignored_present_generated_local_path_count": len(unignored_present),
            "suspicious_top_level_entry_count": len(suspicious),
            "terminal_output_artifact_count": terminal_count,
            "total_generated_local_bytes_estimate": total_bytes,
            "coverage_artifact_present": any(item["path"] == "coverage.xml" and item["exists"] for item in candidates),
            "egg_info_present": any(item["path"] == "eduboost.egg-info" and item["exists"] for item in candidates),
            "local_backup_path_count": sum(1 for item in present if item["artifact_class"] == "local_backup"),
        },
        "cleanup_policy": {
            "audit_only": True,
            "no_cleanup_performed": True,
            "generated_local_cleanup_authorised": False,
            "file_deletion_authorised": False,
            "artifact_deletion_authorised": False,
            "repository_history_rewrite_authorised": False,
            "prd0_closure_deferred_to_prd010": True,
        },
        "authority_boundaries": {
            "runtime_kg_implementation_claimed": True,
            "runtime_kg_authority_switch_authorised": True,
            "authority_switch_executed": True,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "public_beta_live_traffic_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
            "new_kg_slice_authorised": False,
            "prd1_implementation_authorised": False,
        },
    }


def audit(root: Path = Path(".")) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    register = read_json(root / REGISTER)
    record = read_json(root / RECORD)
    saved_inventory = read_json(root / INVENTORY)
    current_inventory = repository_hygiene_inventory(root)
    prd008 = evaluate_prd008(root)

    for path in [PRD_DOC, PLAN, SCHEMA_DOC, RECORD, POLICY_DOC]:
        if not (root / path).exists():
            errors.append(f"missing required PRD-0.9 file: {path}")
    if prd008.get("valid") is not True:
        errors.append("PRD-0.8 verifier must be valid before PRD-0.9")
    if register.get("last_recorded_item") not in {"PRD-0.8", "PRD-0.9"}:
        errors.append("production readiness register must be positioned at PRD-0.8 or PRD-0.9")
    if register.get("last_recorded_item") == "PRD-0.8" and register.get("next_authorised_item") != PRD_ID:
        errors.append("production readiness register must authorise PRD-0.9 after PRD-0.8")
    for key in TRUE_KEYS:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
    for key in FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
    for key in CLEANUP_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
    if record.get("no_cleanup_performed") is not True:
        errors.append("no_cleanup_performed must be true")
    if record.get("no_file_deletion_performed") is not True:
        errors.append("no_file_deletion_performed must be true")
    if record.get("prd0_closure_deferred_to_prd010") is not True:
        errors.append("prd0_closure_deferred_to_prd010 must be true")

    policy_doc_ok = current_inventory.get("repository_hygiene_policy_document_refreshed") is True
    authority_valid = (
        not errors
        and record.get("prd008_branch_release_naming_reconciliation_valid") is True
        and record.get("repository_hygiene_policy_document_refreshed") is True
        and record.get("cleanup_recommendation_recorded") is True
        and record.get("suspicious_top_level_entries_inventory_required") is True
        and policy_doc_ok
    )

    recorded = record.get("repository_hygiene_generated_local_artifact_audit_recorded") is True
    inventory_recorded = (
        record.get("generated_local_artifact_inventory_recorded") is True
        and saved_inventory.get("schema_version") == "prd-repository-hygiene-generated-local-artifact-audit/v1"
        and saved_inventory.get("prd_id") == PRD_ID
    )
    final_valid = (
        authority_valid
        and recorded
        and inventory_recorded
        and record.get("next_authorised_item") == "PRD-0.10"
        and register.get("last_recorded_item") == PRD_ID
        and register.get("next_authorised_item") == "PRD-0.10"
        and record.get("no_cleanup_performed") is True
        and record.get("no_file_deletion_performed") is True
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-0.9 authority is valid but evidence capture has not completed")

    summary = current_inventory.get("summary", {})
    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "errors": errors,
        "warnings": warnings,
        "prd008_branch_release_naming_reconciliation_valid": prd008.get("valid") is True,
        "repository_hygiene_generated_local_artifact_audit_recorded": recorded,
        "generated_local_artifact_inventory_recorded": inventory_recorded,
        "repository_hygiene_policy_document_refreshed": policy_doc_ok,
        "configured_generated_local_path_count": summary.get("configured_generated_local_path_count", 0),
        "present_generated_local_path_count": summary.get("present_generated_local_path_count", 0),
        "ignored_present_generated_local_path_count": summary.get("ignored_present_generated_local_path_count", 0),
        "unignored_present_generated_local_path_count": summary.get("unignored_present_generated_local_path_count", 0),
        "suspicious_top_level_entry_count": summary.get("suspicious_top_level_entry_count", 0),
        "terminal_output_artifact_count": summary.get("terminal_output_artifact_count", 0),
        "coverage_artifact_present": summary.get("coverage_artifact_present", False),
        "egg_info_present": summary.get("egg_info_present", False),
        "generated_local_cleanup_authorised": record.get("generated_local_cleanup_authorised") is True,
        "file_deletion_authorised": record.get("file_deletion_authorised") is True,
        "artifact_deletion_authorised": record.get("artifact_deletion_authorised") is True,
        "repository_history_rewrite_authorised": record.get("repository_history_rewrite_authorised") is True,
        "no_cleanup_performed": record.get("no_cleanup_performed") is True,
        "no_file_deletion_performed": record.get("no_file_deletion_performed") is True,
        "prd0_closure_deferred_to_prd010": record.get("prd0_closure_deferred_to_prd010") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed") is True,
        "runtime_kg_authority_switch_authorised": record.get("runtime_kg_authority_switch_authorised") is True,
        "authority_switch_executed": record.get("authority_switch_executed") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "public_beta_live_traffic_authorised": record.get("public_beta_live_traffic_authorised") is True,
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised") is True,
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True,
        "new_kg_slice_authorised": record.get("new_kg_slice_authorised") is True,
        "prd1_implementation_authorised": record.get("prd1_implementation_authorised") is True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.9 valid: {result['valid']}")
        print(f"PRD-0.9 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
