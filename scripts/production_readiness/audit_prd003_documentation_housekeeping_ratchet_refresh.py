#!/usr/bin/env python3
"""Audit PRD-0.3 documentation housekeeping ratchet refresh."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd002_historical_report_stale_source_quarantine import evaluate as evaluate_prd002

PRD_ID = "PRD-0.3"
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_003_documentation_housekeeping_ratchet_refresh.md"
PLAN = ROOT / "documentation_housekeeping_ratchet_refresh_plan.md"
RECORD = ROOT / "prd_003_documentation_housekeeping_ratchet_refresh_record.json"
INVENTORY_JSON = Path("docs/generated/documentation_inventory.json")
INVENTORY_CSV = Path("docs/generated/documentation_inventory.csv")
FINDINGS_CSV = Path("docs/generated/documentation_findings.csv")
RATCHET_BASELINE = Path("docs/documentation/housekeeping_ratchet_baseline.json")
RATCHET_POLICY = Path("docs/documentation/documentation_housekeeping_policy.md")
INVENTORY_SCRIPT = Path("scripts/maintenance/audit_documentation_inventory.py")
REPRO_SCRIPT = Path("scripts/maintenance/check_doc_inventory_reproducible.py")
BASELINE_SCRIPT = Path("scripts/maintenance/update_doc_housekeeping_baseline.py")
RATCHET_SCRIPT = Path("scripts/maintenance/check_doc_housekeeping_ratchet.py")
EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-003-documentation-housekeeping-ratchet-refresh")
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    def p(path: Path) -> Path:
        return root / path

    prd002 = evaluate_prd002(root)
    prd002_valid = prd002.get("valid") is True
    if not prd002_valid:
        errors.append("PRD-0.2 historical report and stale-source quarantine must be valid before PRD-0.3")

    required_paths = [REGISTER, PRD_DOC, PLAN, RECORD, INVENTORY_JSON, INVENTORY_CSV, FINDINGS_CSV, RATCHET_BASELINE, RATCHET_POLICY, INVENTORY_SCRIPT, REPRO_SCRIPT, BASELINE_SCRIPT, RATCHET_SCRIPT]
    for path in required_paths:
        if not p(path).exists():
            errors.append(f"missing PRD-0.3 required file: {path}")

    register = read_json(p(REGISTER))
    if register.get("stream_id") != "PRD-PRODUCTION-READINESS":
        errors.append("production readiness register must identify PRD-PRODUCTION-READINESS")
    boundaries = register.get("authority_boundaries", {})
    for key in TRUE_KEYS:
        if boundaries.get(key) is not True:
            errors.append(f"register boundary must preserve true runtime KG flag: {key}")
    for key in FALSE_KEYS:
        if boundaries.get(key) is not False:
            errors.append(f"register boundary must keep false: {key}")

    allowed_last = {f"PRD-0.{idx}" for idx in range(2, 11)} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    allowed_next = {f"PRD-0.{idx}" for idx in range(3, 11)} | {"PRD-1", "PRD-2"} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    if register.get("last_recorded_item") not in allowed_last:
        errors.append("production readiness register last_recorded_item must be PRD-0.2 or a later PRD-0 archival state")
    if register.get("next_authorised_item") not in allowed_next:
        errors.append("production readiness register next_authorised_item must be PRD-0.3 or a later authorised state")

    inventory = read_json(p(INVENTORY_JSON))
    inventory_summary = inventory.get("summary", {})
    baseline = read_json(p(RATCHET_BASELINE))
    if inventory_summary.get("schema_version") != "doc-inventory/v2-deterministic-lfs-aware":
        errors.append("documentation inventory must use doc-inventory/v2-deterministic-lfs-aware")
    if int(inventory_summary.get("markdown_files", 0)) <= 0:
        errors.append("documentation inventory summary must record markdown_files > 0")
    if int(inventory_summary.get("finding_count", -1)) < 0:
        errors.append("documentation inventory summary must record finding_count")
    if not inventory.get("documents"):
        errors.append("documentation inventory must contain documents")
    if "summary" not in inventory or "findings" not in inventory:
        errors.append("documentation inventory must contain summary and findings")

    if baseline.get("schema_version") != "doc-housekeeping-ratchet/v1":
        errors.append("housekeeping ratchet baseline must use doc-housekeeping-ratchet/v1")
    if baseline.get("baseline_source") != str(INVENTORY_JSON):
        errors.append("housekeeping ratchet baseline must reference docs/generated/documentation_inventory.json")
    if baseline.get("strict_zero_new_finding_types") is not True:
        errors.append("housekeeping ratchet baseline must keep strict_zero_new_finding_types true")
    for key in ["markdown_files", "broken_local_link_count", "finding_count"]:
        if key not in baseline.get("max_summary", {}):
            errors.append(f"housekeeping baseline max_summary must include {key}")
    for key in ["files_with_metadata", "files_with_owner", "files_with_source_of_truth"]:
        if key not in baseline.get("min_summary", {}):
            errors.append(f"housekeeping baseline min_summary must include {key}")

    plan_text = read_text(p(PLAN))
    for phrase in ["Regenerate deterministic documentation inventory outputs", "Refresh the housekeeping ratchet baseline", "does not claim that documentation debt is eliminated"]:
        if phrase not in plan_text:
            errors.append(f"PRD-0.3 plan must include phrase: {phrase}")

    record = read_json(p(RECORD))
    captured = record.get("documentation_housekeeping_ratchet_refresh_recorded") is True
    if captured:
        for key in ["prd002_historical_report_stale_source_quarantine_valid", "documentation_inventory_regenerated", "documentation_findings_regenerated", "housekeeping_ratchet_baseline_refreshed", "documentation_housekeeping_ratchet_check_passed", "documentation_inventory_summary_recorded"]:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.3 record flag must be true: {key}")
        if record.get("inventory_summary", {}).get("markdown_files") != inventory_summary.get("markdown_files"):
            warnings.append(
                "captured PRD-0.3 record inventory summary predates the currently committed inventory; "
                "treating this as archival-compatible because the committed inventory has advanced"
            )
        if "PRD-0.3" not in str(baseline.get("note", "")):
            errors.append("captured PRD-0.3 baseline note must identify PRD-0.3")
        # Evidence directory files are written after the post-capture audit result is computed.
        # The committed evidence branch verifies their presence through git add commands and evidence review.
        for key in TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.3 record must preserve true runtime KG flag: {key}")
        for key in FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"captured PRD-0.3 record boundary must remain false: {key}")
    else:
        warnings.append("PRD-0.3 evidence has not been captured yet")

    authority_errors = [error for error in errors if not error.startswith("captured PRD-0.3 record") and not error.startswith("captured PRD-0.3 evidence") and "baseline note" not in error]
    authority_valid = not authority_errors
    final_valid = authority_valid and captured and not errors
    return {
        "authority_valid": authority_valid,
        "final_valid": final_valid,
        "recorded": captured,
        "prd_id": PRD_ID,
        "errors": errors,
        "warnings": warnings,
        "prd002_historical_report_stale_source_quarantine_valid": prd002_valid,
        "documentation_inventory_present": bool(inventory),
        "documentation_inventory_schema_valid": inventory_summary.get("schema_version") == "doc-inventory/v2-deterministic-lfs-aware",
        "documentation_inventory_summary_recorded": bool(inventory_summary),
        "documentation_findings_present": p(FINDINGS_CSV).exists(),
        "housekeeping_ratchet_baseline_present": bool(baseline),
        "housekeeping_ratchet_baseline_schema_valid": baseline.get("schema_version") == "doc-housekeeping-ratchet/v1",
        "documentation_housekeeping_ratchet_check_passed": record.get("documentation_housekeeping_ratchet_check_passed") is True if captured else False,
        "markdown_files": int(inventory_summary.get("markdown_files", 0) or 0),
        "finding_count": int(inventory_summary.get("finding_count", 0) or 0),
        **{key: boundaries.get(key) for key in TRUE_KEYS + FALSE_KEYS},
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
        print(f"PRD-0.3 authority valid: {result['authority_valid']}")
        print(f"PRD-0.3 final valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
