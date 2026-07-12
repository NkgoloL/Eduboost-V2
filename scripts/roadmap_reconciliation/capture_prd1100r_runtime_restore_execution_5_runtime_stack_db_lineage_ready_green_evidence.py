"""Capture PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5 evidence."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.runtime.runtime_stack_db_ready_green import DEFAULT_OUTPUT_DIR, ROOT, load_runtime_green_summary
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green import audit

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green_record.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-5-runtime-stack-db-lineage-ready-green"
FALSE_BOUNDARIES = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "prd12_implementation_authorised",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _update_register(path: Path, *, now: str, all_green: bool, summary: dict[str, Any]) -> None:
    data = _load(path)
    data.update({
        "status": "prd11_runtime_restore_execution_5_evidence_recorded",
        "last_recorded_at": now,
        "next_authorised_item": NEXT,
        "runtime_restore_execution_5_evidence_recorded": True,
        "runtime_stack_green": all_green,
        "database_lineage_green": summary.get("database_lineage_green") is True,
        "schema_contract_green": summary.get("schema_contract_green") is True,
        "redis_readiness_green": summary.get("redis_readiness_green") is True,
        "ready_probe_green": summary.get("ready_probe_green") is True,
        "runtime_baseline_green": all_green,
        "product_gate_green": False,
        "coverage_gate_green": False,
        "frontend_quality_green": True,
        "generated_contracts_green": True,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
    })
    boundaries = data.get("authority_boundaries") if isinstance(data.get("authority_boundaries"), dict) else {}
    for key in FALSE_BOUNDARIES:
        data[key] = False
        boundaries[key] = False
    data["authority_boundaries"] = boundaries
    _write(path, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-runtime-restore-execution-5-runtime-stack-db-lineage-ready-green", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--runtime-green-summary", type=Path, default=DEFAULT_OUTPUT_DIR / "summary.json")
    parser.add_argument("--require-green", action="store_true", help="Fail unless live runtime stack/DB/Redis//ready evidence is green.")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_execution_5_runtime_stack_db_lineage_ready_green:
        raise SystemExit("missing PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5 claim flag")

    before = audit(ROOT)
    if not before.get("authority_valid"):
        print(json.dumps({"valid": False, "authority_valid": False, "before": before}, indent=2, sort_keys=True))
        return 1

    runtime_summary = _load(args.runtime_green_summary)
    all_green = runtime_summary.get("all_green") is True
    if args.require_green and not all_green:
        print(json.dumps({"valid": False, "authority_valid": True, "runtime_green_required": True, "runtime_summary": runtime_summary}, indent=2, sort_keys=True))
        return 1

    now = datetime.now(timezone.utc).isoformat()
    record = _load(RECORD)
    record.update({
        "evidence_recorded": True,
        "runtime_stack_db_lineage_ready_green_evidence_recorded": True,
        "evidence_recorded_at": now,
        "evidence_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": NEXT,
        "runtime_stack_green": all_green,
        "database_lineage_green": runtime_summary.get("database_lineage_green") is True,
        "schema_contract_green": runtime_summary.get("schema_contract_green") is True,
        "redis_readiness_green": runtime_summary.get("redis_readiness_green") is True,
        "ready_probe_green": runtime_summary.get("ready_probe_green") is True,
        "alembic_upgrade_head_green": runtime_summary.get("alembic_upgrade_head_green") is True,
        "runtime_baseline_green": all_green,
        "product_gate_green": False,
        "coverage_gate_green": False,
        "frontend_quality_green": True,
        "generated_contracts_green": True,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "runtime_green_summary": runtime_summary,
    })
    for key in FALSE_BOUNDARIES:
        record[key] = False
    _write(RECORD, record)
    _update_register(PROD_REGISTER, now=now, all_green=all_green, summary=runtime_summary)
    _update_register(PRD11_REGISTER, now=now, all_green=all_green, summary=runtime_summary)

    summary = {
        "prd_id": PRD_ID,
        "evidence_recorded": True,
        "evidence_recorded_at": now,
        "evidence_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "runtime_stack_green": all_green,
        "database_lineage_green": runtime_summary.get("database_lineage_green") is True,
        "schema_contract_green": runtime_summary.get("schema_contract_green") is True,
        "redis_readiness_green": runtime_summary.get("redis_readiness_green") is True,
        "ready_probe_green": runtime_summary.get("ready_probe_green") is True,
        "alembic_upgrade_head_green": runtime_summary.get("alembic_upgrade_head_green") is True,
        "runtime_baseline_green": all_green,
        "product_gate_green": False,
        "coverage_gate_green": False,
        "frontend_quality_green": True,
        "generated_contracts_green": True,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "next_authorised_item": NEXT,
        "runtime_green_summary": runtime_summary,
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "summary.json", summary)
    _write(EVIDENCE_DIR / "runtime_green_summary.json", runtime_summary)
    if args.runtime_green_summary.exists():
        src_dir = args.runtime_green_summary.parent
        dst_dir = EVIDENCE_DIR / "command-results"
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)

    after = audit(ROOT, require_green=args.require_green)
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0 if (after.get("valid") if args.require_valid else after.get("authority_valid")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
