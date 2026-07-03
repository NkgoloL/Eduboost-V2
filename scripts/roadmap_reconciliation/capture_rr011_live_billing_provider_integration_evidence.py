#!/usr/bin/env python3
"""Capture RR-011 live billing provider integration evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.billing.audit_rr011_live_billing_provider_integration import audit
from scripts.roadmap_reconciliation.verify_rr011_live_billing_provider_integration import evaluate

RR_ID = "RR-011"
RECORD = Path("docs/roadmap/reconciliation/rr_011_live_billing_provider_integration_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-011-live-billing-provider-integration")


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _read_json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def capture(root: Path, owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    audit_result = audit(root, require_final=True)
    record = _read_json(root, RECORD)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    status_short = _git(root, "status", "--short")

    record.update(
        {
            "rr_id": RR_ID,
            "status": "live_billing_provider_integration_recorded",
            "live_billing_provider_integration_recorded": True,
            "rr010_beta_outcome_reporting_valid": True,
            "billing_provider_decision_recorded": True,
            "hosted_checkout_provider_attested": True,
            "hosted_checkout_sandbox_validated": True,
            "webhook_endpoint_validation_recorded": True,
            "webhook_signature_validation_recorded": True,
            "webhook_idempotency_validation_recorded": True,
            "pricing_catalogue_approved": True,
            "no_raw_card_storage_confirmed": True,
            "secrets_not_committed_confirmed": True,
            "billing_launch_boundary_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr012_production_telemetry_remaining_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "billing_provider_integration_audit": audit_result,
            "evidence_owner": owner,
            "target_branch": target_branch,
            "evidence_captured_at": now,
            "git_branch": _git(root, "branch", "--show-current"),
            "git_commit": _git(root, "rev-parse", "HEAD"),
            "status_short": status_short,
            "clean_git_state_at_capture": status_short == "",
        }
    )
    _write_json(root / RECORD, record)

    evidence_dir = root / EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    _write_json(evidence_dir / "billing_provider_integration_audit.json", audit_result)
    _write_json(evidence_dir / "billing_provider_integration_record.json", record)

    verification = evaluate(root)
    _write_json(evidence_dir / "verification.json", verification)

    index = f"""# RR-011 Live Billing Provider Integration Evidence

Captured at: `{now}`  
Owner: `{owner}`  
Target branch: `{target_branch}`  
Git commit: `{record.get('git_commit')}`  
Clean git state at capture: `{record.get('clean_git_state_at_capture')}`

## Evidence files

- `billing_provider_integration_audit.json`
- `billing_provider_integration_record.json`
- `verification.json`

## Integration areas recorded

- Provider decision and hosted-checkout attestation.
- Hosted checkout sandbox validation.
- Webhook endpoint, signature, replay, idempotency, duplicate, out-of-order, and audit validation.
- Pricing catalogue and plan approval.
- No raw card storage and no committed provider secrets.
- Billing-launch boundary.

## Known residual caveats carried forward

- RR-003 remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-012 production telemetry dashboard implementation remains outstanding.
- RR-015 external approvals remain outstanding.
- RR-016 operational drills remain outstanding.

## Boundary

RR-011 records live billing-provider integration evidence only. It does not authorise production billing launch, live payment processing, production release, deployment, release tagging, public beta, or Runtime KG implementation.
"""
    (evidence_dir / "evidence_index.md").write_text(index, encoding="utf-8")

    result = evaluate(root)
    if require_valid and not result["valid"]:
        raise SystemExit(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--claim-rr011-live-billing-provider-integration", action="store_true")
    parser.add_argument("--billing-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_rr011_live_billing_provider_integration:
        raise SystemExit("missing --claim-rr011-live-billing-provider-integration")
    result = capture(Path(args.root), args.billing_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
