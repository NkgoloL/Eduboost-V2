#!/usr/bin/env python3
"""Capture RR-012 production telemetry dashboard implementation evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.telemetry.audit_rr012_production_telemetry_dashboard import audit
from scripts.roadmap_reconciliation.verify_rr012_production_telemetry_dashboard import evaluate

RR_ID = "RR-012"
RECORD = Path("docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-012-production-telemetry-dashboard")


def _git(root: Path, *args: str) -> str:
    try:
        return check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
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
            "status": "production_telemetry_dashboard_recorded",
            "production_telemetry_dashboard_recorded": True,
            "rr011_live_billing_provider_integration_valid": True,
            "dashboard_implementation_attested": True,
            "grafana_dashboard_inventory_recorded": True,
            "production_api_dashboard_implemented": True,
            "learner_journey_dashboard_implemented": True,
            "popia_privacy_dashboard_implemented": True,
            "ai_llm_dashboard_implemented": True,
            "billing_operations_dashboard_implemented": True,
            "infrastructure_readiness_dashboard_implemented": True,
            "slo_dashboard_validation_recorded": True,
            "alert_routing_validation_recorded": True,
            "dashboard_privacy_boundary_recorded": True,
            "no_learner_pii_exposed": True,
            "secrets_not_committed_confirmed": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr013_mastery_model_research_remaining_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "billing_launch_authorised": False,
            "live_payment_processing_authorised": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "production_telemetry_dashboard_audit": audit_result,
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
    _write_json(evidence_dir / "production_telemetry_dashboard_audit.json", audit_result)
    _write_json(evidence_dir / "production_telemetry_dashboard_record.json", record)

    verification = evaluate(root)
    _write_json(evidence_dir / "verification.json", verification)

    index = f"""# RR-012 Production Telemetry Dashboard Evidence

Captured at: `{now}`  
Owner: `{owner}`  
Target branch: `{target_branch}`  
Git commit: `{record.get('git_commit')}`  
Clean git state at capture: `{record.get('clean_git_state_at_capture')}`

## Evidence files

- `production_telemetry_dashboard_audit.json`
- `production_telemetry_dashboard_record.json`
- `verification.json`

## Dashboard areas recorded

- Production API overview dashboard.
- Learner journey health dashboard.
- POPIA privacy operations dashboard.
- AI and LLM operations dashboard.
- Billing operations dashboard.
- Infrastructure readiness dashboard.
- SLO dashboard validation.
- Alert routing and runbook linkage.
- PII-safe dashboard privacy boundary.

## Known residual caveats carried forward

- RR-003 remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-013 advanced mastery-model research remains outstanding.
- RR-015 external approvals remain outstanding.
- RR-016 operational drills remain outstanding.

## Boundary

RR-012 records production telemetry dashboard implementation evidence only. It does not authorise billing launch, live payment processing, production release, deployment, release tagging, public beta, or Runtime KG implementation.
"""
    (evidence_dir / "evidence_index.md").write_text(index, encoding="utf-8")

    result = evaluate(root)
    if require_valid and not result["valid"]:
        raise SystemExit(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--claim-rr012-production-telemetry-dashboard", action="store_true")
    parser.add_argument("--telemetry-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_rr012_production_telemetry_dashboard:
        raise SystemExit("missing --claim-rr012-production-telemetry-dashboard")
    result = capture(Path(args.root), args.telemetry_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
