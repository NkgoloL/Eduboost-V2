"""Capture PRD-11.1R test-suite taxonomy evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd1101r_test_suite_taxonomy_behavioral_gate_overhaul import ROOT, audit
from scripts.test_suites.test_suite_taxonomy import evaluate_taxonomy, suite_commands

RECORD = ROOT / "docs/roadmap/production_readiness/prd_1101r_test_suite_taxonomy_behavioral_gate_overhaul_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
SUMMARY = ROOT / "docs/roadmap/production_readiness/prd11_test_suite_taxonomy_behavioral_gate_overhaul.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/production-readiness/prd-1101r-test-suite-taxonomy-behavioural-gate-overhaul"
TAXONOMY = ROOT / "docs/roadmap/production_readiness/test_suite_taxonomy.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd1101r-test-suite-taxonomy-behavioral-gate-overhaul", action="store_true")
    parser.add_argument("--prd-owner", default="Nkgolo Lebelo")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd1101r_test_suite_taxonomy_behavioral_gate_overhaul:
        raise SystemExit("missing --claim-prd1101r-test-suite-taxonomy-behavioral-gate-overhaul")
    before = audit(ROOT)
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))
    now = datetime.now(timezone.utc).isoformat()

    taxonomy = _load(TAXONOMY)
    taxonomy.update({"status": "evidence_recorded", "last_reviewed_at": now})
    _write(TAXONOMY, taxonomy)

    record = _load(RECORD)
    record.update({
        "status": "test_suite_taxonomy_evidence_recorded",
        "test_suite_taxonomy_evidence_recorded": True,
        "taxonomy_snapshot": evaluate_taxonomy(ROOT),
        "suite_commands": suite_commands(),
        "captured_at": now,
        "prd_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "prd112r_handoff_authorised": True,
        "next_authorised_item": "PRD-11.2R",
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
            "status": "prd11_test_suite_taxonomy_evidence_recorded",
            "last_recorded_item": "PRD-11.1R",
            "last_recorded_at": now,
            "next_authorised_item": "PRD-11.2R",
            "prd11_test_suite_taxonomy_authority_recorded": True,
            "prd11_test_suite_taxonomy_evidence_recorded": True,
            "prd112r_handoff_authorised": True,
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
                if isinstance(item, dict) and item.get("prd_id") == "PRD-11.1R":
                    item.update({"status": "recorded", "authorised": True})
                if isinstance(item, dict) and item.get("prd_id") == "PRD-11.2R":
                    item.update({"status": "authorised_next", "authorised": True})
        _write(path, payload)

    after = audit(ROOT)
    summary = {
        "prd_id": "PRD-11.1R",
        "captured_at": now,
        "valid": after["valid"],
        "authority_valid": after["authority_valid"],
        "next_authorised_item": after["next_authorised_item"],
        "register_next_authorised_item": after["register_next_authorised_item"],
        "production_register_next_authorised_item": after["production_register_next_authorised_item"],
        "taxonomy": after["taxonomy"],
    }
    _write(SUMMARY, summary)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write(EVIDENCE_DIR / "audit_before.json", before)
    _write(EVIDENCE_DIR / "audit_after.json", after)
    _write(EVIDENCE_DIR / "taxonomy.json", after["taxonomy"])
    _write(EVIDENCE_DIR / "suite_commands.json", {"commands": suite_commands()})
    _write(EVIDENCE_DIR / "summary.json", summary)
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))
    print(json.dumps(after, indent=2, sort_keys=True) if args.json else after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
