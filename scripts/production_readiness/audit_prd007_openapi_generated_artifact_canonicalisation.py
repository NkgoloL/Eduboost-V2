#!/usr/bin/env python3
"""Audit PRD-0.7 OpenAPI and generated artifact canonicalisation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd006_workflow_command_hygiene_ci_inventory import evaluate as evaluate_prd006

PRD_ID = "PRD-0.7"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_007_openapi_generated_artifact_canonicalisation.md"
PLAN = ROOT / "openapi_generated_artifact_canonicalisation_plan.md"
SCHEMA_DOC = ROOT / "openapi_generated_artifact_canonicalisation.schema.md"
RECORD = ROOT / "prd_007_openapi_generated_artifact_canonicalisation_record.json"
GENERATED_ARTIFACT_INVENTORY = ROOT / "generated_artifact_canonicalisation_inventory.json"
CANONICAL_OPENAPI = Path("docs/openapi.json")
ROOT_OPENAPI_JSON = Path("openapi.json")
ROOT_OPENAPI_YAML = Path("openapi.yaml")
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_yaml_or_json(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}


def openapi_summary(schema: dict[str, Any]) -> dict[str, Any]:
    paths = schema.get("paths", {}) if isinstance(schema.get("paths"), dict) else {}
    operations = sum(len(value) for value in paths.values() if isinstance(value, dict))
    return {
        "title": schema.get("info", {}).get("title") if isinstance(schema.get("info"), dict) else None,
        "version": schema.get("info", {}).get("version") if isinstance(schema.get("info"), dict) else None,
        "path_count": len(paths),
        "operation_count": operations,
    }


def generated_artifact_inventory(root: Path, captured_at: str | None = None) -> dict[str, Any]:
    canonical_path = root / CANONICAL_OPENAPI
    root_json_path = root / ROOT_OPENAPI_JSON
    root_yaml_path = root / ROOT_OPENAPI_YAML
    canonical = read_json(canonical_path)
    root_json = read_json(root_json_path)
    root_yaml = parse_yaml_or_json(read_text(root_yaml_path))
    generated_paths: list[Path] = []
    for base in [root / "docs" / "generated", root / "docs" / "documentation"]:
        if base.exists():
            generated_paths.extend(p for p in base.rglob("*") if p.is_file())
    historical_snapshots = sorted(str(p.relative_to(root)) for p in (root / "docs").glob("openapi_pr*.json")) if (root / "docs").exists() else []
    generated_artifacts = []
    for p in sorted(generated_paths):
        generated_artifacts.append({
            "path": str(p.relative_to(root)),
            "sha256": sha256(p),
            "size_bytes": p.stat().st_size,
        })
    canonical_sha = sha256(canonical_path)
    root_json_sha = sha256(root_json_path)
    return {
        "schema_version": "prd-openapi-generated-artifact-canonicalisation/v1",
        "prd_id": PRD_ID,
        "captured_at": captured_at,
        "canonical_openapi_path": str(CANONICAL_OPENAPI),
        "root_openapi_json_path": str(ROOT_OPENAPI_JSON),
        "root_openapi_yaml_path": str(ROOT_OPENAPI_YAML),
        "canonical_openapi_present": canonical_path.exists(),
        "root_openapi_json_present": root_json_path.exists(),
        "root_openapi_yaml_present": root_yaml_path.exists(),
        "canonical_openapi_sha256": canonical_sha,
        "root_openapi_json_sha256": root_json_sha,
        "root_openapi_yaml_sha256": sha256(root_yaml_path),
        "root_json_matches_canonical": canonical_path.exists() and root_json_path.exists() and canonical_path.read_text(encoding="utf-8") == root_json_path.read_text(encoding="utf-8"),
        "root_yaml_schema_matches_canonical": bool(canonical) and canonical == root_yaml,
        "canonical_openapi_summary": openapi_summary(canonical),
        "root_openapi_json_summary": openapi_summary(root_json),
        "root_openapi_yaml_summary": openapi_summary(root_yaml),
        "openapi_path_count": openapi_summary(canonical)["path_count"],
        "openapi_operation_count": openapi_summary(canonical)["operation_count"],
        "historical_openapi_snapshots": historical_snapshots,
        "historical_openapi_snapshot_count": len(historical_snapshots),
        "generated_artifact_count": len(generated_artifacts),
        "generated_artifacts": generated_artifacts,
        "canonicalisation_policy": {
            "canonical_openapi_source": "docs/openapi.json",
            "root_openapi_json_is_generated_mirror": True,
            "root_openapi_yaml_is_generated_mirror": True,
            "historical_openapi_snapshots_are_non_canonical": True,
            "branch_release_naming_reconciliation_deferred_to_prd008": True,
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
    prd006 = evaluate_prd006(root)
    if not prd006.get("valid"):
        errors.append("PRD-0.6 workflow command hygiene and CI inventory must be valid before PRD-0.7")
    register = read_json(root / REGISTER)
    allowed_last = {f"PRD-0.{idx}" for idx in range(6, 11)} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    allowed_next = {f"PRD-0.{idx}" for idx in range(7, 11)} | {"PRD-1"} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    if register.get("last_recorded_item") not in allowed_last:
        errors.append("production readiness register last_recorded_item must be PRD-0.6 or a later PRD-0 archival state")
    if register.get("next_authorised_item") not in allowed_next:
        errors.append("production readiness register next_authorised_item must be PRD-0.7 or a later authorised state")
    for path in [PRD_DOC, PLAN, SCHEMA_DOC, RECORD]:
        if not (root / path).exists():
            errors.append(f"missing PRD-0.7 authority file: {path}")
    record = read_json(root / RECORD)
    inventory = read_json(root / GENERATED_ARTIFACT_INVENTORY)
    live_inventory = generated_artifact_inventory(root)
    current_inventory = inventory or live_inventory
    recorded = record.get("openapi_generated_artifact_canonicalisation_recorded") is True
    inventory_recorded = bool(inventory) and inventory.get("schema_version") == "prd-openapi-generated-artifact-canonicalisation/v1"
    root_json_matches = current_inventory.get("root_json_matches_canonical") is True
    root_yaml_matches = current_inventory.get("root_yaml_schema_matches_canonical") is True
    canonical_summary = current_inventory.get("canonical_openapi_summary", {})
    path_count = int(current_inventory.get("openapi_path_count") or canonical_summary.get("path_count") or 0)
    operation_count = int(current_inventory.get("openapi_operation_count") or canonical_summary.get("operation_count") or 0)
    historical_snapshots_retained = int(current_inventory.get("historical_openapi_snapshot_count") or 0) >= 0 and record.get("historical_openapi_snapshots_retained") is True
    branch_deferred = record.get("branch_release_naming_reconciliation_deferred_to_prd008") is True or current_inventory.get("canonicalisation_policy", {}).get("branch_release_naming_reconciliation_deferred_to_prd008") is True
    for key in TRUE_KEYS:
        if record.get(key) is not True:
            errors.append(f"{key} must remain true")
    for key in FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"{key} must remain false")
    authority_valid = (
        not errors
        and record.get("prd006_workflow_command_hygiene_ci_inventory_valid") is True
        and record.get("canonical_openapi_source_of_truth_recorded") is True
        and record.get("root_openapi_json_mirror_recorded") is True
        and record.get("root_openapi_yaml_mirror_recorded") is True
        and branch_deferred
    )
    final_valid = (
        authority_valid
        and recorded
        and inventory_recorded
        and root_json_matches
        and root_yaml_matches
        and path_count > 0
        and operation_count > 0
        and historical_snapshots_retained
        and record.get("openapi_mirrors_canonicalised") is True
    )
    if authority_valid and not final_valid:
        warnings.append("PRD-0.7 authority is valid but evidence capture has not completed")
    return {
        "valid": final_valid,
        "authority_valid": authority_valid,
        "errors": errors,
        "warnings": warnings,
        "prd_id": PRD_ID,
        "prd006_workflow_command_hygiene_ci_inventory_valid": prd006.get("valid") is True,
        "openapi_generated_artifact_canonicalisation_recorded": recorded,
        "generated_artifact_inventory_recorded": inventory_recorded,
        "canonical_openapi_path": current_inventory.get("canonical_openapi_path"),
        "root_openapi_json_path": current_inventory.get("root_openapi_json_path"),
        "root_openapi_yaml_path": current_inventory.get("root_openapi_yaml_path"),
        "root_json_matches_canonical": root_json_matches,
        "root_yaml_schema_matches_canonical": root_yaml_matches,
        "openapi_path_count": path_count,
        "openapi_operation_count": operation_count,
        "generated_artifact_count": int(current_inventory.get("generated_artifact_count") or 0),
        "historical_openapi_snapshot_count": int(current_inventory.get("historical_openapi_snapshot_count") or 0),
        "canonical_openapi_source_of_truth_recorded": record.get("canonical_openapi_source_of_truth_recorded") is True,
        "root_openapi_json_mirror_recorded": record.get("root_openapi_json_mirror_recorded") is True,
        "root_openapi_yaml_mirror_recorded": record.get("root_openapi_yaml_mirror_recorded") is True,
        "openapi_mirrors_canonicalised": record.get("openapi_mirrors_canonicalised") is True,
        "branch_release_naming_reconciliation_deferred_to_prd008": branch_deferred,
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed") is True,
        "runtime_kg_authority_switch_authorised": record.get("runtime_kg_authority_switch_authorised") is True,
        "authority_switch_executed": record.get("authority_switch_executed") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
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
        print(f"PRD-0.7 valid: {result['valid']}")
        print(f"PRD-0.7 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
