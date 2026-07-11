"""Capture PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3 evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd1100r_runtime_restore_execution_3_generated_contract_frontend_green_run import ROOT, NEXT, PRD_ID, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_3_generated_contract_frontend_green_run_record.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_runtime_restore_execution_3_generated_contract_frontend_green_run.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1100r-runtime-restore-execution-3-generated-contract-frontend-green-run"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _update_register(path: Path, *, now: str) -> None:
    payload = _load(path)
    payload["next_authorised_item"] = NEXT
    payload["last_recorded_item"] = PRD_ID
    payload["last_recorded_at"] = now
    payload["runtime_restore_execution_3_evidence_recorded"] = True
    payload["generated_contracts_green"] = False
    payload["frontend_quality_green"] = False
    payload["runtime_baseline_green"] = False
    payload["controlled_beta_activation_operational_hold"] = True
    payload["live_learner_traffic_operationally_safe"] = False
    payload["production_release_evidence_blocked_until_runtime_baseline_green"] = True
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
        payload[key] = False
        if isinstance(payload.get("authority_boundaries"), dict):
            payload["authority_boundaries"][key] = False
    _write(path, payload)


def capture(*, owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    authority = audit(ROOT)
    if require_valid and not authority.get("authority_valid"):
        raise SystemExit("PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3 authority is not valid")
    now = datetime.now(timezone.utc).isoformat()
    record = _load(RECORD)
    record.update({
        "evidence_recorded": True,
        "captured_at": now,
        "evidence_owner": owner,
        "target_branch": target_branch,
        "generated_contracts_green": False,
        "frontend_quality_green": False,
        "runtime_baseline_green": False,
        "next_authorised_item": NEXT,
    })
    _write(RECORD, record)
    _update_register(PROD_REGISTER, now=now)
    _update_register(PRD11_REGISTER, now=now)
    summary = {
        "prd_id": PRD_ID,
        "valid": False,
        "authority_valid": authority.get("authority_valid") is True,
        "captured_at": now,
        "owner": owner,
        "target_branch": target_branch,
        "generated_contracts_green": False,
        "frontend_quality_green": False,
        "runtime_baseline_green": False,
        "controlled_beta_activation_operational_hold": True,
        "live_learner_traffic_operationally_safe": False,
        "next_authorised_item": NEXT,
    }
    _write(SUMMARY, summary)
    _write(EVIDENCE_DIR / "summary.json", summary)
    _write(EVIDENCE_DIR / "record.json", record)
    post = audit(ROOT)
    summary["valid"] = post.get("valid") is True
    summary["authority_valid"] = post.get("authority_valid") is True
    summary["audit"] = post
    _write(SUMMARY, summary)
    _write(EVIDENCE_DIR / "summary.json", summary)
    _write(EVIDENCE_DIR / "record.json", record)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1100r-runtime-restore-execution-3-generated-contract-frontend-green-run", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1100r_runtime_restore_execution_3_generated_contract_frontend_green_run:
        raise SystemExit("Explicit PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3 claim flag is required")
    result = capture(owner=args.prd_owner, target_branch=args.target_branch, require_valid=args.require_valid)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
