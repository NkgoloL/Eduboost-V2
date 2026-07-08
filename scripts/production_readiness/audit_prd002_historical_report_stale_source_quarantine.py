#!/usr/bin/env python3
"""Audit PRD-0.2 historical report and stale-source quarantine."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_prd001_canonical_current_state_documentation_refresh import evaluate as evaluate_prd001

PRD_ID = "PRD-0.2"
PRD001_RECORD = Path("docs/roadmap/production_readiness/prd_001_canonical_current_state_documentation_refresh_record.json")
ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD_DOC = ROOT / "prd_002_historical_report_stale_source_quarantine.md"
RECORD = ROOT / "prd_002_historical_report_stale_source_quarantine_record.json"
REPORTS_README = Path("docs/reports/README.md")
QUARANTINE_REGISTER = Path("docs/reports/stale_source_quarantine_register.json")
HISTORICAL_REPORT = Path("docs/reports/EduBoost_V2_True_Status_Report_2026-07-03.md")
ZONE_IDENTIFIER = Path("docs/reports/EduBoost_V2_True_Status_Report_2026-07-03.md:Zone.Identifier")
TRUE_KEYS = ["runtime_kg_implementation_claimed", "runtime_kg_authority_switch_authorised", "authority_switch_executed"]
FALSE_KEYS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "public_beta_live_traffic_authorised", "live_learner_traffic_authorised", "billing_launch_authorised", "live_payment_processing_authorised", "new_kg_slice_authorised", "prd1_implementation_authorised"]
CURRENT_AUTHORITY_SOURCES = [
    "docs/current_state.md",
    "docs/roadmap/production_readiness/production_readiness_register.json",
    "docs/roadmap/production_readiness/current_state_documentation_truth_map.json",
    "docs/roadmap/reconciliation/final_roadmap_reconciliation_closure_record.json",
    "docs/roadmap/knowledge_graph/kg_roadmap_closure_record.json",
]
REQUIRED_REPORT_PHRASES = [
    "Historical report — superseded",
    "**not** a live roadmap, release, KG, RR, PRD, production-readiness, public-beta, billing, deployment, or runtime-authority source of truth",
    "Do **not** use historical RR/KG status tables in this report to decide current implementation order",
    "quarantined_by: PRD-0.2",
    "status: historical-superseded",
]
REQUIRED_README_PHRASES = ["historical reports", "Do not treat files in this directory as current roadmap authority", "stale_source_quarantine_register.json"]

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

    prd001 = evaluate_prd001(root)
    prd001_record = read_json(p(PRD001_RECORD))
    prd001_record_valid = (
        prd001_record.get("canonical_current_state_documentation_refresh_recorded") is True
        and prd001_record.get("verification", {}).get("valid") is True
    )
    prd001_valid = prd001.get("valid") is True or prd001_record_valid
    if not prd001_valid:
        errors.append("PRD-0.1 canonical current-state documentation refresh verifier or captured record must be valid before PRD-0.2")

    for path in [REGISTER, PRD_DOC, RECORD, REPORTS_README, QUARANTINE_REGISTER, HISTORICAL_REPORT]:
        if not p(path).exists():
            errors.append(f"missing PRD-0.2 file: {path}")
    if p(ZONE_IDENTIFIER).exists():
        errors.append("Windows Zone.Identifier report sidecar must be removed/quarantined outside the repo")

    register = read_json(p(REGISTER))
    boundaries = register.get("authority_boundaries", {})
    if register.get("stream_id") != "PRD-PRODUCTION-READINESS":
        errors.append("production readiness register must identify PRD-PRODUCTION-READINESS")
    ALLOWED_LAST_RECORDED_ITEMS = {f"PRD-0.{idx}" for idx in range(1, 11)} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    ALLOWED_NEXT_AUTHORISED_ITEMS = {f"PRD-0.{idx}" for idx in range(2, 11)} | {"PRD-1"} | {f"PRD-1.{idx}" for idx in range(0, 10)}
    if register.get("last_recorded_item") not in ALLOWED_LAST_RECORDED_ITEMS:
        errors.append("production readiness register last_recorded_item must be a valid PRD-0.x state")
    if register.get("next_authorised_item") not in ALLOWED_NEXT_AUTHORISED_ITEMS:
        errors.append("production readiness register next_authorised_item must be a valid PRD-0.x state, or PRD-1 after PRD-0.10 closure")
    for key in TRUE_KEYS:
        if boundaries.get(key) is not True:
            errors.append(f"register boundary must preserve true runtime KG flag: {key}")
    for key in FALSE_KEYS:
        if boundaries.get(key) is not False:
            errors.append(f"register boundary must keep false: {key}")

    qreg = read_json(p(QUARANTINE_REGISTER))
    if qreg.get("register_id") != "STALE-SOURCE-QUARANTINE-REGISTER":
        errors.append("stale-source quarantine register must identify STALE-SOURCE-QUARANTINE-REGISTER")
    if qreg.get("current_authority_sources") != CURRENT_AUTHORITY_SOURCES:
        errors.append("stale-source quarantine register must list current authority sources in order")
    sources = qreg.get("quarantined_sources", [])
    if not sources:
        errors.append("stale-source quarantine register must list at least one quarantined source")
    else:
        source = sources[0]
        if source.get("path") != str(HISTORICAL_REPORT):
            errors.append("quarantined source path must be the July 2026 true-status report")
        if source.get("status") != "historical_superseded":
            errors.append("quarantined source status must be historical_superseded")
        if source.get("source_of_truth") is not False:
            errors.append("quarantined source must not be a source of truth")
        if source.get("superseded_by") != CURRENT_AUTHORITY_SOURCES:
            errors.append("quarantined source must be superseded by the current authority sources")
    if qreg.get("windows_zone_identifier_policy", {}).get("tracked_zone_identifier_files_allowed") is not False:
        errors.append("stale-source register must forbid tracked Zone.Identifier sidecars")

    report_text = read_text(p(HISTORICAL_REPORT))
    for phrase in REQUIRED_REPORT_PHRASES:
        if phrase not in report_text:
            errors.append(f"historical report must include quarantine phrase: {phrase}")
    readme_text = read_text(p(REPORTS_README))
    for phrase in REQUIRED_README_PHRASES:
        if phrase not in readme_text:
            errors.append(f"reports README must include quarantine phrase: {phrase}")

    record = read_json(p(RECORD))
    captured = record.get("historical_report_stale_source_quarantine_recorded") is True
    if captured:
        for key in ["prd001_canonical_current_state_documentation_refresh_valid", "stale_source_quarantine_register_recorded", "historical_reports_marked_superseded", "stale_roadmap_authority_blocked", "zone_identifier_removed", "current_authority_sources_recorded"]:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.2 record flag must be true: {key}")
        for key in TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"captured PRD-0.2 record must preserve true runtime KG flag: {key}")
        for key in FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"captured PRD-0.2 record boundary must remain false: {key}")
    else:
        warnings.append("PRD-0.2 evidence has not been captured yet")

    authority_errors = [e for e in errors if not e.startswith("captured PRD-0.2 record")]
    authority_valid = not authority_errors
    final_valid = authority_valid and captured and not errors
    return {
        "authority_valid": authority_valid,
        "final_valid": final_valid,
        "recorded": captured,
        "prd_id": PRD_ID,
        "errors": errors,
        "warnings": warnings,
        "prd001_canonical_current_state_documentation_refresh_valid": prd001_valid,
        "stale_source_quarantine_register_recorded": bool(qreg),
        "historical_reports_marked_superseded": not any("historical report must include" in e for e in errors),
        "stale_roadmap_authority_blocked": not any("source of truth" in e for e in errors),
        "zone_identifier_removed": not p(ZONE_IDENTIFIER).exists(),
        "current_authority_sources_recorded": qreg.get("current_authority_sources") == CURRENT_AUTHORITY_SOURCES,
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
        print(f"PRD-0.2 authority valid: {result['authority_valid']}")
        print(f"PRD-0.2 final valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["authority_valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
