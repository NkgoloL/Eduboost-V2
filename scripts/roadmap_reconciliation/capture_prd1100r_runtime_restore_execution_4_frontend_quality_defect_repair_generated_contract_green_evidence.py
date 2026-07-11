"""Capture PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4 evidence."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.advisory_suites.generated_contract_frontend_quality_green_evidence import DEFAULT_OUTPUT_DIR, ROOT, load_green_evidence_summary
from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence import audit

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4"
NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence_record.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-4-frontend-quality-defect-repair-generated-contract-green-evidence"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _update_register(path: Path, *, now: str, all_green: bool) -> None:
    data = _load(path)
    data.update({
        "status": "prd11_runtime_restore_execution_4_evidence_recorded",
        "last_recorded_at": now,
        "next_authorised_item": NEXT,
        "runtime_restore_execution_4_evidence_recorded": True,
        "generated_contracts_green": all_green,
        "frontend_quality_green": all_green,
        "runtime_baseline_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
    })
    boundaries = data.get("authority_boundaries") if isinstance(data.get("authority_boundaries"), dict) else {}
    for key in (
        "production_release_authorised",
        "deployment_authorised",
        "release_tag_authorised",
        "public_beta_authorised",
        "public_beta_live_traffic_authorised",
        "billing_launch_authorised",
        "live_payment_processing_authorised",
        "prd12_implementation_authorised",
    ):
        data[key] = False
        boundaries[key] = False
    data["authority_boundaries"] = boundaries
    _write(path, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-runtime-restore-execution-4-frontend-quality-defect-repair-generated-contract-green-evidence", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--green-run-summary", type=Path, default=DEFAULT_OUTPUT_DIR / "summary.json")
    parser.add_argument("--require-green", action="store_true", help="Fail unless the real green-run summary reports all gates green.")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_execution_4_frontend_quality_defect_repair_generated_contract_green_evidence:
        raise SystemExit("missing PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4 claim flag")

    before = audit(ROOT)
    if not before.get("authority_valid"):
        print(json.dumps({"valid": False, "authority_valid": False, "before": before}, indent=2, sort_keys=True))
        return 1

    green_summary = _load(args.green_run_summary)
    all_green = green_summary.get("all_green") is True
    if args.require_green and not all_green:
        print(json.dumps({"valid": False, "authority_valid": True, "green_run_required": True, "green_summary": green_summary}, indent=2, sort_keys=True))
        return 1

    now = datetime.now(timezone.utc).isoformat()
    record = _load(RECORD)
    record.update({
        "evidence_recorded": True,
        "evidence_recorded_at": now,
        "evidence_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "next_authorised_item": NEXT,
        "generated_contracts_green": all_green,
        "frontend_quality_green": all_green,
        "runtime_baseline_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "green_run_summary": green_summary,
    })
    _write(RECORD, record)
    _update_register(PROD_REGISTER, now=now, all_green=all_green)
    _update_register(PRD11_REGISTER, now=now, all_green=all_green)

    summary = {
        "prd_id": PRD_ID,
        "evidence_recorded": True,
        "evidence_recorded_at": now,
        "evidence_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "generated_contracts_green": all_green,
        "frontend_quality_green": all_green,
        "runtime_baseline_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "production_release_evidence_blocked_until_runtime_baseline_green": True,
        "next_authorised_item": NEXT,
        "green_run_summary": green_summary,
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "summary.json", summary)
    _write(EVIDENCE_DIR / "green_run_summary.json", green_summary)
    if args.green_run_summary.exists():
        src_dir = args.green_run_summary.parent
        dst_dir = EVIDENCE_DIR / "command-results"
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)

    after = audit(ROOT, require_green=args.require_green)
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0 if (after.get("valid") if args.require_valid else after.get("authority_valid")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
