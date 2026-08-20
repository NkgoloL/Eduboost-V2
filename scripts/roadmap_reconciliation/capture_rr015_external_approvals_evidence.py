#!/usr/bin/env python3
"""Capture RR-015 external approvals evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.approvals.audit_rr015_external_approvals import audit

RR_ID = "RR-015"
RR014_RECORD = Path("docs/roadmap/reconciliation/rr_014_public_beta_expansion_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_015_external_approvals_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-015-external-approvals")


def _run(root: Path, cmd: list[str]) -> str:
    try:
        return check_output(cmd, cwd=root, text=True, stderr=subprocess.STDOUT).strip()
    except Exception:
        return ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def capture(root: Path, owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    audit_result = audit(root, require_final=True)
    rr014 = _json(root, RR014_RECORD)
    rr014_valid = rr014.get("public_beta_expansion_readiness_recorded") is True
    branch = _run(root, ["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit = _run(root, ["git", "rev-parse", "HEAD"])
    status_short = _run(root, ["git", "status", "--short"])
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    valid = audit_result.get("valid") is True and rr014_valid and status_short == ""

    record = {
        "rr_id": RR_ID,
        "status": "external_approvals_recorded" if valid else "external_approvals_invalid",
        "external_approvals_recorded": valid,
        "rr014_public_beta_expansion_valid": rr014_valid,
        "security_review_approved": valid,
        "popia_privacy_review_approved": valid,
        "legal_review_approved": valid,
        "caps_content_review_approved": valid,
        "release_owner_go_no_go_signoff_recorded": valid,
        "external_approval_boundary_recorded": valid,
        "repository_only_approval_substitution_blocked": valid,
        "rr003_fallback_coverage_caveat_visible": True,
        "rr006_non_required_checks_caveat_visible": True,
        "rr016_operational_drills_remaining_visible": True,
        "rr017_release_safety_controls_remaining_visible": True,
        "rr018_trustworthy_beta_quality_remaining_visible": True,
        "public_beta_expansion_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "expanded_learner_data_migration_authorised": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "target_branch": target_branch,
        "git_branch": branch,
        "git_commit": commit,
        "clean_git_state_at_capture": status_short == "",
        "evidence_owner": owner,
        "evidence_captured_at": now,
        "external_approvals_audit": audit_result,
    }
    (root / RECORD).parent.mkdir(parents=True, exist_ok=True)
    (root / RECORD).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence_dir = root / EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "rr015_external_approvals_audit.json").write_text(
        json.dumps(audit_result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence_dir / "rr015_external_approvals_record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence_dir / "evidence_index.md").write_text(
        f"""# RR-015 External Approvals Evidence Index

- RR ID: `{RR_ID}`
- Captured at: `{now}`
- Owner: `{owner}`
- Target branch: `{target_branch}`
- Git branch: `{branch}`
- Git commit: `{commit}`
- Clean git state at capture: `{status_short == ''}`
- Valid: `{valid}`

## Evidence files

- `rr015_external_approvals_audit.json`
- `rr015_external_approvals_record.json`

## Boundary

RR-015 records external approval evidence only. It does not authorise public beta launch/live traffic, expanded learner migration, production release, deployment, release tagging, billing launch, live payment processing, or runtime KG implementation.
""",
        encoding="utf-8",
    )
    result = {
        "valid": valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "evidence_dir": str(EVIDENCE_DIR),
        "clean_git_state_at_capture": status_short == "",
        "status_short": status_short,
        "rr014_public_beta_expansion_valid": rr014_valid,
        "external_approvals_recorded": valid,
        "security_review_approved": valid,
        "popia_privacy_review_approved": valid,
        "legal_review_approved": valid,
        "caps_content_review_approved": valid,
        "release_owner_go_no_go_signoff_recorded": valid,
        "public_beta_expansion_authorised": False,
        "production_release_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "errors": audit_result.get("errors", []),
    }
    if require_valid and not valid:
        return result
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--claim-rr015-external-approvals", action="store_true")
    parser.add_argument("--approvals-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_rr015_external_approvals:
        raise SystemExit("missing --claim-rr015-external-approvals")
    result = capture(Path(args.root), args.approvals_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
