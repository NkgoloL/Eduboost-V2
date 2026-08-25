#!/usr/bin/env python3
"""Capture RR-005 technical debt burn-down evidence."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_rr005_technical_debt_burndown import evaluate as verify_rr005
from scripts.technical_debt.audit_rr005_technical_debt import evaluate as audit_rr005

RR_ID = "RR-005"
RECORD = Path("docs/roadmap/reconciliation/rr_005_technical_debt_burndown_record.json")
EVIDENCE_DIR = Path("docs/release-evidence/roadmap-reconciliation/rr-005-technical-debt-burndown")

BOUNDARY_FALSE = {
    "production_release_authorised": False,
    "deployment_authorised": False,
    "release_tag_authorised": False,
    "public_beta_authorised": False,
    "runtime_kg_implementation_claimed": False,
}


def _run_git(args: list[str], root: Path) -> dict[str, Any]:
    completed = run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return {
        "command": ["git", *args],
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_index(root: Path, record: dict[str, Any], audit_path: Path) -> None:
    index = root / EVIDENCE_DIR / "evidence_index.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(
        "\n".join(
            [
                "# RR-005 Technical Debt Burn-Down Evidence",
                "",
                f"**RR item:** {RR_ID}",
                f"**Recorded at:** {record['recorded_at']}",
                f"**Owner:** {record['technical_debt_owner']}",
                f"**Valid:** {str(record['technical_debt_burndown_recorded']).lower()}",
                "",
                "## Evidence files",
                "",
                f"- `{RECORD}`",
                f"- `{audit_path.relative_to(root)}`",
                "",
                "## Captured checks",
                "",
                f"- Ruff debt captured: `{record['ruff_debt_captured']}`",
                f"- Import-linter exceptions registered: `{record['import_linter_exceptions_registered']}`",
                f"- Stale route comments audited: `{record['stale_route_comments_audited']}`",
                f"- Migration history audited: `{record['migration_history_audited']}`",
                f"- Dormant router review recorded: `{record['dormant_router_review_recorded']}`",
                f"- Debt burn-down backlog recorded: `{record['debt_burndown_backlog_recorded']}`",
                "",
                "## Residual caveats carried forward",
                "",
                "- RR-003 remains valid but used fallback coverage and recorded `0.0` because full test collection had pre-existing blockers.",
                "- RR-006 evidence landed while only the required branch-protection check was blocking; some non-required checks were red at merge time.",
                "",
                "## Boundaries",
                "",
                "- Production release remains unauthorised.",
                "- Deployment remains unauthorised.",
                "- Public beta remains unauthorised.",
                "- Runtime KG implementation remains unclaimed.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def capture(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    audit = audit_rr005(root)
    git_branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    git_head = _run_git(["rev-parse", "HEAD"], root)
    git_status = _run_git(["status", "--short"], root)
    clean = git_status["returncode"] == 0 and git_status["stdout"] == ""

    record = {
        "rr_id": RR_ID,
        "recorded_at": datetime.now(UTC).isoformat(),
        "technical_debt_owner": args.technical_debt_owner,
        "target_branch": args.target_branch,
        "clean_git_state_at_capture": clean,
        "git_state": {
            "branch": git_branch["stdout"] if git_branch["returncode"] == 0 else None,
            "head_sha": git_head["stdout"] if git_head["returncode"] == 0 else None,
            "status_short": git_status["stdout"] if git_status["returncode"] == 0 else None,
            "target_branch": args.target_branch,
        },
        "technical_debt_burndown_recorded": bool(args.claim_rr005_technical_debt_burndown and audit["valid"]),
        "ruff_debt_captured": bool(audit["checks"].get("ruff_debt_inventory_collected")),
        "import_linter_exceptions_registered": bool(audit["checks"].get("import_linter_exceptions_registered")),
        "stale_route_comments_audited": bool(audit["checks"].get("stale_route_comments_audited")),
        "migration_history_audited": bool(audit["checks"].get("migration_history_audited")),
        "dormant_router_review_recorded": bool(audit["checks"].get("dormant_router_review_recorded")),
        "debt_burndown_backlog_recorded": True,
        "rr003_fallback_coverage_caveat_visible": True,
        "rr006_non_required_checks_caveat_visible": True,
        "technical_debt_audit": audit,
        **BOUNDARY_FALSE,
    }
    _write_json(root / RECORD, record)
    audit_path = root / EVIDENCE_DIR / "raw" / "rr005_technical_debt_audit.json"
    _write_json(audit_path, audit)
    _write_index(root, record, audit_path)
    verification = verify_rr005(root)
    record["valid"] = verification["valid"]
    record["verification_errors"] = verification["errors"]
    _write_json(root / RECORD, record)
    _write_index(root, record, audit_path)
    return {**verification, "record": record, "audit_path": str(audit_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-rr005-technical-debt-burndown", action="store_true")
    parser.add_argument("--technical-debt-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = capture(Path(args.root), args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"RR-005 valid: {result['valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    if args.require_valid and not result["valid"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
