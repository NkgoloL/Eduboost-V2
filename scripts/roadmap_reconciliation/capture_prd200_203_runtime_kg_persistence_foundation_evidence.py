"""Capture PRD-2.0-2.3 runtime KG persistence foundation evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd200_203_runtime_kg_persistence_foundation import ROOT, audit

PRD_ID = "PRD-2.0-2.3"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_200_203_runtime_kg_persistence_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd2_runtime_kg_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-200-203-runtime-kg-persistence-foundation"
EVIDENCE_JSON = ROOT / "docs/roadmap/production_readiness/prd2_runtime_kg_persistence_foundation.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    before = audit(ROOT)
    if require_valid and not before.get("authority_valid"):
        raise SystemExit("PRD-2.0-2.3 authority is not valid; refusing to capture evidence")
    now = datetime.now(UTC).isoformat()
    record = _load(RECORD)
    register = _load(REGISTER)
    prod_register = _load(PROD_REGISTER)

    record.update(
        {
            "status": "recorded",
            "runtime_kg_persistence_foundation_recorded": True,
            "recorded_at": now,
            "recorded_by": owner,
            "target_branch": target_branch,
            "next_authorised_item": "PRD-2.4-2.6",
            "prd2_4_2_6_authorised": True,
            "prd3_implementation_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "live_learner_traffic_authorised": False,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
        }
    )
    register.update(
        {
            "status": "runtime_kg_persistence_foundation_recorded",
            "last_recorded_item": PRD_ID,
            "last_recorded_at": now,
            "next_authorised_item": "PRD-2.4-2.6",
            "runtime_kg_persistence_foundation_recorded": True,
            "runtime_kg_foundation_recorded_at": now,
        }
    )
    for entry in register.get("prd2_sequence", []):
        if entry.get("prd_id") == "PRD-2.0-2.3":
            entry["status"] = "recorded"
            entry["authorised"] = True
        if entry.get("prd_id") == "PRD-2.4-2.6":
            entry["status"] = "authorised"
            entry["authorised"] = True

    prod_register.update(
        {
            "status": "prd2_runtime_kg_persistence_foundation_recorded",
            "last_recorded_item": PRD_ID,
            "last_recorded_at": now,
            "next_authorised_item": "PRD-2.4-2.6",
            "prd2_runtime_kg_persistence_foundation_recorded": True,
            "prd2_next_authorised_item": "PRD-2.4-2.6",
            "prd3_implementation_authorised": False,
        }
    )
    prod_register.setdefault("current_truth", {})["prd2_runtime_kg_persistence_foundation_recorded"] = True
    prod_register["current_truth"]["prd2_next_authorised_item"] = "PRD-2.4-2.6"
    prod_register.setdefault("authority_boundaries", {})["prd3_implementation_authorised"] = False

    _write(RECORD, record)
    _write(REGISTER, register)
    _write(PROD_REGISTER, prod_register)

    after = audit(ROOT)
    evidence = {
        "prd_id": PRD_ID,
        "captured_at": now,
        "captured_by": owner,
        "target_branch": target_branch,
        "authority_before_capture": before,
        "final_verification": after,
        "evidence_files": {
            "record_sha256": _sha256(RECORD),
            "register_sha256": _sha256(REGISTER),
            "production_register_sha256": _sha256(PROD_REGISTER),
        },
    }
    _write(EVIDENCE_JSON, evidence)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "evidence.json", evidence)
    (EVIDENCE_DIR / "SHA256SUMS.txt").write_text(
        "\n".join(
            [
                f"{_sha256(RECORD)}  {RECORD.relative_to(ROOT)}",
                f"{_sha256(REGISTER)}  {REGISTER.relative_to(ROOT)}",
                f"{_sha256(PROD_REGISTER)}  {PROD_REGISTER.relative_to(ROOT)}",
                f"{_sha256(EVIDENCE_JSON)}  {EVIDENCE_JSON.relative_to(ROOT)}",
            ]
        )
        + "\n"
    )
    if require_valid and not after.get("valid"):
        raise SystemExit("PRD-2.0-2.3 final verifier is not valid after capture")
    return after


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd200-203-runtime-kg-persistence-foundation", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd200_203_runtime_kg_persistence_foundation:
        raise SystemExit("explicit PRD-2.0-2.3 claim flag is required")
    result = capture(args.prd_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{PRD_ID}: valid={result['valid']} authority_valid={result['authority_valid']}")


if __name__ == "__main__":
    main()
