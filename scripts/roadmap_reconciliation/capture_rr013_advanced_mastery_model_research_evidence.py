#!/usr/bin/env python3
"""Capture RR-013 advanced mastery-model research evidence."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import datetime as dt
import json
from scripts._subprocess import check_output, run
from pathlib import Path
from typing import Any

from scripts.mastery_research.audit_rr013_advanced_mastery_model_research import audit

RR_ID = "RR-013"
RECORD = Path("docs/roadmap/reconciliation/rr_013_advanced_mastery_model_research_record.json")
RR012_RECORD = Path("docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-013-advanced-mastery-model-research")


def _git(root: Path, *args: str) -> str:
    try:
        return check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def capture(root: Path | str, owner: str, target_branch: str, require_valid: bool) -> dict[str, Any]:
    root = Path(root)
    audit_result = audit(root, require_final=True)
    status_short = _git(root, "status", "--short")
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD") or target_branch
    commit = _git(root, "rev-parse", "HEAD")
    rr012 = _json(root / RR012_RECORD)
    rr012_valid = rr012.get("production_telemetry_dashboard_recorded") is True

    valid = audit_result.get("valid") is True and rr012_valid
    if require_valid and status_short:
        valid = False

    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    record = _json(root / RECORD)
    record.update(
        {
            "rr_id": RR_ID,
            "status": "advanced_mastery_model_research_recorded" if valid else "advanced_mastery_model_research_invalid",
            "advanced_mastery_model_research_recorded": valid,
            "rr012_production_telemetry_dashboard_valid": rr012_valid,
            "research_only_boundary_recorded": True,
            "existing_mastery_model_preserved": True,
            "literature_review_recorded": valid,
            "model_candidates_compared": valid,
            "evaluation_protocol_recorded": valid,
            "data_readiness_ethics_reviewed": valid,
            "caps_alignment_evaluation_required": True,
            "human_review_required_before_deployment": True,
            "no_learner_pii_exported_for_research": True,
            "runtime_kg_north_star_boundary_preserved": True,
            "research_decision_memo_recorded": valid,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr014_public_beta_expansion_remaining_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "model_deployment_authorised": False,
            "learner_facing_model_change_authorised": False,
            "production_learner_data_retraining_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "public_beta_authorised": False,
            "evidence_owner": owner,
            "evidence_captured_at": now,
            "git_branch": branch,
            "target_branch": target_branch,
            "git_commit": commit,
            "clean_git_state_at_capture": status_short == "",
            "advanced_mastery_model_research_audit": audit_result,
        }
    )
    (root / RECORD).parent.mkdir(parents=True, exist_ok=True)
    (root / RECORD).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    evidence_dir = root / EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "rr013_advanced_mastery_model_research_audit.json").write_text(
        json.dumps(audit_result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence_dir / "rr013_advanced_mastery_model_research_record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence_dir / "evidence_index.md").write_text(
        f"""# RR-013 Advanced Mastery-Model Research Evidence Index\n\n- RR ID: `{RR_ID}`\n- Captured at: `{now}`\n- Owner: `{owner}`\n- Target branch: `{target_branch}`\n- Git branch: `{branch}`\n- Git commit: `{commit}`\n- Clean git state at capture: `{status_short == ''}`\n- Valid: `{valid}`\n\n## Evidence files\n\n- `rr013_advanced_mastery_model_research_audit.json`\n- `rr013_advanced_mastery_model_research_record.json`\n\n## Boundary\n\nRR-013 records research only. It does not authorise runtime KG implementation, learner-facing model deployment, model retraining on production learner data, production release, deployment, release tagging, or public beta.\n""",
        encoding="utf-8",
    )
    return {
        "valid": valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "evidence_dir": str(EVIDENCE_DIR),
        "clean_git_state_at_capture": status_short == "",
        "status_short": status_short,
        "rr012_production_telemetry_dashboard_valid": rr012_valid,
        "advanced_mastery_model_research_recorded": valid,
        "runtime_kg_implementation_claimed": False,
        "model_deployment_authorised": False,
        "production_release_authorised": False,
        "public_beta_authorised": False,
        "errors": audit_result.get("errors", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--claim-rr013-advanced-mastery-model-research", action="store_true")
    parser.add_argument("--research-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_rr013_advanced_mastery_model_research:
        raise SystemExit("missing --claim-rr013-advanced-mastery-model-research")
    result = capture(Path(args.root), args.research_owner, args.target_branch, args.require_valid)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
