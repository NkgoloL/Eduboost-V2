#!/usr/bin/env python3
"""Capture RR-010 beta outcome reporting evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.beta_outcomes.audit_rr010_beta_outcome_reporting import audit
from scripts.roadmap_reconciliation.verify_rr010_beta_outcome_reporting import evaluate

RR_ID = "RR-010"
RECORD = Path("docs/roadmap/reconciliation/rr_010_beta_outcome_reporting_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-010-beta-outcome-reporting")


def _git(root: Path, *args: str) -> str:
    try:
        return check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def capture(root: Path, owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    record_path = root / RECORD
    record = json.loads(record_path.read_text(encoding="utf-8"))
    audit_result = audit(root, require_final=True)
    if not audit_result.get("final_outputs_valid"):
        raise SystemExit(json.dumps(audit_result, indent=2, sort_keys=True))

    status_short = _git(root, "status", "--short")
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    metrics = audit_result.get("metrics_summary", {})

    record.update(
        {
            "rr_id": RR_ID,
            "status": "beta_outcome_reporting_recorded",
            "beta_outcome_reporting_recorded": True,
            "minimum_beta_duration_met": True,
            "cohort_size_requirement_met": True,
            "educator_feedback_collected": True,
            "uptime_target_met": True,
            "p95_diagnostic_latency_target_met": True,
            "zero_critical_security_incidents": True,
            "zero_pii_exposure_events": True,
            "zero_consent_incidents": True,
            "educator_content_approval_threshold_met": True,
            "learner_session_completion_threshold_met": True,
            "backup_restore_drill_references_recorded": True,
            "weekly_health_reviews_completed": True,
            "beta_outcome_report_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "beta_outcome_audit": audit_result,
            "beta_metrics_summary": metrics,
            "evidence_captured_at": now,
            "evidence_owner": owner,
            "target_branch": target_branch,
            "git_commit": _git(root, "rev-parse", "HEAD"),
            "git_branch": _git(root, "branch", "--show-current"),
            "status_short": status_short,
            "clean_git_state_at_capture": status_short == "",
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "runtime_kg_implementation_claimed": False,
        }
    )
    _write_json(record_path, record)

    verification = evaluate(root)
    evidence_dir = root / EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    _write_json(evidence_dir / "beta_outcome_audit.json", audit_result)
    _write_json(evidence_dir / "verification.json", verification)
    _write_json(evidence_dir / "beta_metrics_summary.json", metrics)
    index = f"""# RR-010 Beta Outcome Reporting Evidence

**RR item:** RR-010  
**Captured at:** {now}  
**Owner:** {owner}  
**Target branch:** {target_branch}  
**Git commit:** {record.get('git_commit')}  
**Clean git state at capture:** {record.get('clean_git_state_at_capture')}  

## Evidence files

- `beta_outcome_audit.json`
- `beta_metrics_summary.json`
- `verification.json`

## Outcome areas recorded

- Minimum beta duration and cohort size metrics.
- Educator feedback and content approval threshold.
- Uptime and p95 diagnostic latency threshold.
- Critical security, PII exposure, and consent incident summary.
- Learner session completion threshold.
- Backup/restore drill references.
- Weekly beta health reviews.
- Final beta outcome report.

## Known residual caveats carried forward

- RR-003 remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-015 external approvals remain outstanding.
- RR-016 operational drills remain outstanding as their own register item, even though RR-010 must reference backup/restore drill evidence.

## Boundary

RR-010 records controlled beta outcome reporting only. It does not authorise production release, deployment, release tagging, public beta, or runtime KG implementation.
"""
    (evidence_dir / "evidence_index.md").write_text(index, encoding="utf-8")

    result = evaluate(root)
    if require_valid and not result["valid"]:
        raise SystemExit(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--claim-rr010-beta-outcome-reporting", action="store_true")
    parser.add_argument("--outcome-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_rr010_beta_outcome_reporting:
        raise SystemExit("missing --claim-rr010-beta-outcome-reporting")
    result = capture(Path(args.root), args.outcome_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
