"""Capture a current-state, self-reviewed governance refresh for Execution-8.

This is deliberately separate from the historical PRD-11.1R/11.2R/11.3R
capture scripts. Those scripts advance an older register sequence and must not
be used when the canonical registers already authorize Execution-8.

The command is dry-run by default. ``--apply`` writes four contract snapshots,
refreshes the four independently reviewed contract timestamps/statuses, and
records digest-bound B01 manual evidence with the actual checkout branch and
source commit. It does not claim Execution-8 completion or authorize release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts._subprocess import run_git
from scripts.true_state_remediation.core import (
    atomic_write_json,
    record_manual_evidence,
    root_from,
    sha256_file,
)

CONTRACTS = (
    ("test_suite_taxonomy", "docs/roadmap/production_readiness/test_suite_taxonomy.json"),
    ("script_taxonomy", "docs/roadmap/production_readiness/script_taxonomy.json"),
    ("coverage_contract", "docs/roadmap/production_readiness/coverage_contract.json"),
    ("product_runtime_test_gate_contract", "docs/roadmap/production_readiness/product_runtime_test_gate_contract.json"),
)
EXPECTED_NEXT = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8"
SELF_REVIEWER = "Nkgolo Lebelo"
SELF_REVIEW_ROLE = "Lead Engineer (Self-Review)"
SELF_REVIEW_NOTES = (
    "Completed self-review of current Execution-8 governance contract evidence. "
    "Conflict disclosed: sole developer; not independent approval."
)
FALSE_BOUNDARIES = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
)


def _git(root: Path, *args: str) -> str:
    result = run_git(*args, repo_root=root, check=True)
    return result.stdout.strip()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_json(path, payload)


def _review_payload(root: Path, key: str, relative: str, now: str, branch: str, commit: str) -> dict[str, Any]:
    path = root / relative
    payload = _load(path)
    payload.update({
        "status": "evidence_recorded",
        "last_reviewed_at": now,
        "execution8_governance_refresh": True,
        "execution8_review_branch": branch,
        "execution8_review_commit": commit,
    })
    return {
        "contract_id": key,
        "contract_path": relative,
        "contract_sha256": sha256_file(path),
        "reviewed_contract": payload,
    }


def _check_registers(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in (
        "docs/roadmap/production_readiness/production_readiness_register.json",
        "docs/roadmap/production_readiness/prd11_production_release_register.json",
    ):
        payload = _load(root / relative)
        if payload.get("next_authorised_item") != EXPECTED_NEXT:
            errors.append(f"{relative}: next_authorised_item is not {EXPECTED_NEXT}")
        boundaries = payload.get("authority_boundaries", {})
        for key in FALSE_BOUNDARIES:
            if payload.get(key) is not False or boundaries.get(key) is not False:
                errors.append(f"{relative}: release boundary {key} is not false")
    return errors


def build_report(root: Path) -> dict[str, Any]:
    branch = _git(root, "branch", "--show-current") or "DETACHED"
    commit = _git(root, "rev-parse", "HEAD")
    errors = _check_registers(root)
    contracts = []
    for key, relative in CONTRACTS:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing contract: {relative}")
            continue
        contracts.append({
            "contract_id": key,
            "contract_path": relative,
            "current_sha256": sha256_file(path),
            "current_last_reviewed_at": _load(path).get("last_reviewed_at"),
        })
    return {
        "schema_version": "eduboost/execution8-governance-refresh/v1",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "execution8_next_authorised_item": EXPECTED_NEXT,
        "reviewer": SELF_REVIEWER,
        "reviewer_role": SELF_REVIEW_ROLE,
        "review_notes": SELF_REVIEW_NOTES,
        "branch": branch,
        "source_commit": commit,
        "release_boundaries_preserved_false": True,
        "register_errors": errors,
        "contracts": contracts,
        "valid_for_apply": not errors and branch != "DETACHED",
    }


def apply(root: Path, report: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    if not report["valid_for_apply"]:
        raise SystemExit(json.dumps(report, indent=2, sort_keys=True))
    now = report["reviewed_at"]
    branch = report["branch"]
    commit = report["source_commit"]
    output_dir.mkdir(parents=True, exist_ok=True)
    applied = []
    for key, relative in CONTRACTS:
        review = _review_payload(root, key, relative, now, branch, commit)
        snapshot = output_dir / f"{key}.json"
        _write(snapshot, review)
        control = f"EXECUTION-8-GOV-{len(applied) + 1:02d}"
        manual_path = record_manual_evidence(
            root,
            "B01",
            control,
            reviewer=SELF_REVIEWER,
            reviewer_role=SELF_REVIEW_ROLE,
            decision="completed",
            artifact_path=str(snapshot),
            notes=f"{SELF_REVIEW_NOTES} Branch: {branch}. Source commit: {commit}.",
        )
        payload = _load(root / relative)
        payload.update({
            "status": "evidence_recorded",
            "last_reviewed_at": now,
            "execution8_governance_refresh": True,
            "execution8_review_branch": branch,
            "execution8_review_commit": commit,
        })
        _write(root / relative, payload)
        manual = _load(manual_path)
        manual.update({"review_branch": branch, "review_commit": commit})
        _write(manual_path, manual)
        applied.append({
            "contract_id": key,
            "control_id": control,
            "snapshot": str(snapshot.relative_to(root)),
            "snapshot_sha256": sha256_file(snapshot),
            "manual_evidence": str(manual_path.relative_to(root)),
        })
    final = {**report, "applied": applied}
    _write(output_dir / "summary.json", final)
    return final


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output-dir", default="docs/release-evidence/true-state-remediation/execution8-governance-refresh")
    args = parser.parse_args()
    root = root_from(Path(args.repo))
    report = build_report(root)
    if not args.apply:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["valid_for_apply"] else 1
    result = apply(root, report, root / args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
