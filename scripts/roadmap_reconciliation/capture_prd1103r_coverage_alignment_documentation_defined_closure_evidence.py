"""Capture PRD-11.3R coverage alignment evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.coverage_suites.coverage_contract import evaluate_coverage_contract, coverage_commands
from scripts.production_readiness.audit_prd1103r_coverage_alignment_documentation_defined_closure import ROOT, audit

RECORD = ROOT / "docs/roadmap/production_readiness/prd_1103r_coverage_alignment_documentation_defined_closure_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_contract.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_coverage_alignment_documentation_defined_closure.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1103r-coverage-alignment-documentation-defined-closure"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1103r-coverage-alignment-documentation-defined-closure", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1103r_coverage_alignment_documentation_defined_closure:
        raise SystemExit("missing --claim-prd1103r-coverage-alignment-documentation-defined-closure")
    before = audit(ROOT)
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()

    contract = _load(CONTRACT)
    contract.update({"status": "evidence_recorded", "last_reviewed_at": now})
    _write(CONTRACT, contract)

    record = _load(RECORD)
    record.update({
        "status": "coverage_alignment_evidence_recorded",
        "coverage_alignment_evidence_recorded": True,
        "coverage_contract_snapshot": evaluate_coverage_contract(ROOT),
        "coverage_commands": coverage_commands(),
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "runtime_restore_handoff_authorised": True,
        "next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE",
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
    })
    _write(RECORD, record)

    for path in (REGISTER, PROD_REGISTER):
        payload = _load(path)
        payload.update({
            "status": "prd11_coverage_alignment_evidence_recorded",
            "last_recorded_item": "PRD-11.3R",
            "last_recorded_at": now,
            "next_authorised_item": "PRD-11.0R.RUNTIME-RESTORE",
            "prd11_coverage_alignment_authority_recorded": True,
            "prd11_coverage_alignment_evidence_recorded": True,
            "runtime_restore_handoff_authorised": True,
        })
        payload.setdefault("authority_boundaries", {})
        if isinstance(payload.get("authority_boundaries"), dict):
            payload["authority_boundaries"].update({
                "production_release_authorised": False,
                "deployment_authorised": False,
                "release_tag_authorised": False,
                "public_beta_authorised": False,
                "public_beta_live_traffic_authorised": False,
                "billing_launch_authorised": False,
                "live_payment_processing_authorised": False,
            })
        if path == REGISTER:
            seq = payload.setdefault("prd11_sequence", [])
            for item in seq:
                if isinstance(item, dict) and item.get("prd_id") == "PRD-11.3R":
                    item.update({"status": "recorded", "authorised": True})
                if isinstance(item, dict) and item.get("prd_id") == "PRD-11.0R.RUNTIME-RESTORE":
                    item.update({"status": "authorised_next", "authorised": True})
        _write(path, payload)

    provisional = audit(ROOT)
    summary = {
        "prd_id": "PRD-11.3R",
        "captured_at": now,
        "authority_valid": provisional["authority_valid"],
        "coverage_contract_valid": provisional["coverage_contract_valid"],
        "next_authorised_item": provisional["next_authorised_item"],
        "register_next_authorised_item": provisional["register_next_authorised_item"],
        "production_register_next_authorised_item": provisional["production_register_next_authorised_item"],
        "coverage_contract": provisional["coverage_contract"],
    }
    _write(SUMMARY, summary)
    after = audit(ROOT)
    summary["valid"] = after["valid"]
    summary["authority_valid"] = after["authority_valid"]
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "coverage_contract.json", after["coverage_contract"])
    _write(EVIDENCE_DIR / "coverage_commands.json", {"commands": coverage_commands()})
    _write(EVIDENCE_DIR / "summary.json", summary)
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
