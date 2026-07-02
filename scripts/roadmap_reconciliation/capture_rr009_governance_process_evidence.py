#!/usr/bin/env python3
"""Capture RR-009 governance/process reconciliation evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.governance.audit_rr009_governance_process import audit
from scripts.roadmap_reconciliation.verify_rr009_governance_process import evaluate

RR_ID = "RR-009"
RECORD = Path("docs/roadmap/reconciliation/rr_009_governance_process_reconciliation_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-009-governance-process-reconciliation")


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def capture(root: Path, owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    record_path = root / RECORD
    record = json.loads(record_path.read_text(encoding="utf-8"))
    audit_result = audit(root)
    status_short = _git(root, "status", "--short")
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    record.update(
        {
            "rr_id": RR_ID,
            "status": "governance_process_reconciliation_recorded",
            "governance_process_reconciliation_recorded": True,
            "current_state_refresh_cadence_recorded": True,
            "adr_index_completed": True,
            "external_todo_ownership_recorded": True,
            "branch_protection_release_docs_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr010_beta_outcome_reporting_remaining_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "governance_process_audit": audit_result,
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
    _write_json(evidence_dir / "governance_process_audit.json", audit_result)
    _write_json(evidence_dir / "verification.json", verification)
    index = f"""# RR-009 Governance Process Reconciliation Evidence

**RR item:** RR-009  
**Captured at:** {now}  
**Owner:** {owner}  
**Target branch:** {target_branch}  
**Git commit:** {record.get('git_commit')}  
**Clean git state at capture:** {record.get('clean_git_state_at_capture')}  

## Evidence files

- `governance_process_audit.json`
- `verification.json`

## Governance/process areas recorded

- `docs/current_state.md` refresh cadence
- ADR index completion
- External TODO ownership and dates
- Branch protection reflected in canonical release docs

## Known residual caveats carried forward

- RR-003 remains valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-010 beta outcome reporting remains outstanding.
- RR-015 external approvals remain outstanding.
- RR-016 operational drills remain outstanding.

## Boundary

RR-009 records governance/process reconciliation only. It does not authorise production release, deployment, release tagging, public beta, or runtime KG implementation.
"""
    (evidence_dir / "evidence_index.md").write_text(index, encoding="utf-8")

    result = evaluate(root)
    if require_valid and not result["valid"]:
        raise SystemExit(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--claim-rr009-governance-process", action="store_true")
    parser.add_argument("--governance-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_rr009_governance_process:
        raise SystemExit("missing --claim-rr009-governance-process")
    result = capture(Path(args.root), args.governance_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
