#!/usr/bin/env python3
"""Capture Phase 18 controlled beta launch-governance evidence.

This is not a launch activation gate. It verifies the Phase 17 readiness baseline
and the launch-operations pack, then records that launch governance is ready for
review while all release/deployment/live-traffic boundaries remain false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from scripts._subprocess import run
from datetime import datetime, timezone
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_18_controlled_beta_launch_governance_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/runtime-readiness/phase-18-controlled-beta-launch-governance")
PHASE17_VERIFIER = pathlib.Path("scripts/runtime_readiness/verify_controlled_beta_readiness.py")
REQUIRED_OPERATION_DOCS: tuple[str, ...] = (
    "docs/operations/beta/controlled_beta_launch_governance.md",
    "docs/operations/beta/controlled_beta_candidate_cohort_manifest.template.json",
    "docs/operations/beta/controlled_beta_consent_pack_checklist.md",
    "docs/operations/beta/controlled_beta_support_runbook.md",
    "docs/operations/beta/controlled_beta_incident_response_runbook.md",
    "docs/operations/beta/controlled_beta_rollback_plan.md",
    "docs/operations/beta/controlled_beta_observability_plan.md",
    "docs/operations/beta/controlled_beta_data_handling_register.md",
)
FALSE_BOUNDARY_FIELDS: tuple[str, ...] = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "controlled_beta_launch_authorised",
    "live_learner_traffic_authorised",
    "learner_data_migration_authorised",
    "runtime_kg_implementation_claimed",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_cmd(args: list[str]) -> tuple[int, str, str]:
    try:
        proc = run(args, check=False, text=True, capture_output=True)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def boundary_payload() -> dict[str, bool | str]:
    return {
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "controlled_beta_launch_authorised": False,
        "live_learner_traffic_authorised": False,
        "learner_data_migration_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "scope": "controlled_beta_launch_governance_only",
    }


def collect_git_state(target_branch: str) -> dict[str, Any]:
    rc_head, head, err_head = run_cmd(["git", "rev-parse", "HEAD"])
    rc_branch, branch, _ = run_cmd(["git", "branch", "--show-current"])
    rc_diff, _, _ = run_cmd(["git", "diff", "--quiet"])
    rc_cached, _, _ = run_cmd(["git", "diff", "--cached", "--quiet"])
    rc_remote, remote, err_remote = run_cmd(["git", "rev-parse", f"origin/{target_branch}"])
    rc_status, status, _ = run_cmd(["git", "status", "--short"])
    head_sha = head.strip() if rc_head == 0 else None
    remote_sha = remote.strip() if rc_remote == 0 else None
    return {
        "branch": branch.strip() if rc_branch == 0 else None,
        "head_sha": head_sha,
        "target_branch": target_branch,
        "remote_target_sha": remote_sha,
        "head_matches_remote_target": bool(head_sha and remote_sha and head_sha == remote_sha),
        "tracked_worktree_clean_before_capture": rc_diff == 0 and rc_cached == 0,
        "git_status_short": status.splitlines(),
        "errors": [e for e in (err_head.strip(), err_remote.strip()) if e],
    }


def run_phase17_verifier() -> dict[str, Any]:
    if not PHASE17_VERIFIER.exists():
        return {"name": "controlled_beta_readiness", "script": PHASE17_VERIFIER.as_posix(), "returncode": 2, "valid": False, "stderr": "verifier missing", "payload": {}}
    rc, stdout, stderr = run_cmd(["python3", PHASE17_VERIFIER.as_posix(), "--json"])
    payload: dict[str, Any]
    try:
        parsed = json.loads(stdout)
        payload = parsed if isinstance(parsed, dict) else {"raw": parsed}
    except Exception:
        payload = {"stdout": stdout}
    return {
        "name": "controlled_beta_readiness",
        "script": PHASE17_VERIFIER.as_posix(),
        "returncode": rc,
        "valid": rc == 0 and payload.get("valid") is True,
        "payload": payload,
        "stderr": stderr,
    }


def validate_operation_docs() -> dict[str, Any]:
    docs: list[dict[str, Any]] = []
    errors: list[str] = []
    for rel in REQUIRED_OPERATION_DOCS:
        path = pathlib.Path(rel)
        if not path.exists():
            errors.append(f"missing launch operation document: {rel}")
            docs.append({"path": rel, "exists": False})
            continue
        text = path.read_text(encoding="utf-8")
        markers = ["Phase 18", "controlled beta", "not authorise"]
        missing = [m for m in markers if m.lower() not in text.lower()]
        if len(text.strip()) < 250:
            errors.append(f"launch operation document is too short: {rel}")
        if missing:
            errors.append(f"launch operation document missing markers {missing}: {rel}")
        docs.append({
            "path": rel,
            "exists": True,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "missing_markers": missing,
        })
    return {"valid": len(errors) == 0, "documents": docs, "errors": errors, "required": list(REQUIRED_OPERATION_DOCS)}


def build_result(*, claimed: bool, phase17: dict[str, Any], git_state: dict[str, Any], documents: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not claimed:
        errors.append("controlled beta launch governance must be explicitly claimed")
    if phase17.get("valid") is not True:
        errors.append("Phase 17 controlled beta readiness verifier must be valid")
    if documents.get("valid") is not True:
        errors.extend(documents.get("errors") or ["launch operation documents must be valid"])
    if git_state.get("tracked_worktree_clean_before_capture") is not True:
        errors.append("tracked worktree must be clean before Phase 18 launch-governance capture")
    if git_state.get("head_matches_remote_target") is not True:
        warnings.append("HEAD does not match origin target branch; final master evidence should be captured from protected master")
    return {
        "valid": len(errors) == 0,
        "controlled_beta_launch_governance_recorded": len(errors) == 0,
        "controlled_beta_launch_governance_claimed": claimed,
        "phase_17_controlled_beta_readiness_valid": phase17.get("valid") is True,
        "launch_operations_documents_valid": documents.get("valid") is True,
        "errors": errors,
        "warnings": warnings,
        **boundary_payload(),
    }


def write_evidence_index(path: pathlib.Path, record: dict[str, Any], result: dict[str, Any], phase17: dict[str, Any], documents: dict[str, Any]) -> None:
    lines = [
        "# Phase 18 Controlled Beta Launch Governance Evidence",
        "",
        f"Captured at: {record['captured_at']}",
        f"Governance owner: {record['governance_owner']}",
        f"Source commit: {record['source_commit']}",
        f"Target branch: {record['target_branch']}",
        "",
        "## Governance Inputs",
        "",
        f"- Phase 17 controlled beta readiness valid: {str(result['phase_17_controlled_beta_readiness_valid']).lower()}",
        f"- Launch operations documents valid: {str(result['launch_operations_documents_valid']).lower()}",
        f"- Controlled beta launch governance recorded: {str(result['controlled_beta_launch_governance_recorded']).lower()}",
        "",
        "## Explicit Boundary",
        "",
        f"- Production release authorised: {str(record['production_release_authorised']).lower()}",
        f"- Deployment authorised: {str(record['deployment_authorised']).lower()}",
        f"- Release tag authorised: {str(record['release_tag_authorised']).lower()}",
        f"- Public beta authorised: {str(record['public_beta_authorised']).lower()}",
        f"- Controlled beta launch authorised: {str(record['controlled_beta_launch_authorised']).lower()}",
        f"- Live learner traffic authorised: {str(record['live_learner_traffic_authorised']).lower()}",
        f"- Learner data migration authorised: {str(record['learner_data_migration_authorised']).lower()}",
        f"- Runtime KG implementation claimed: {str(record['runtime_kg_implementation_claimed']).lower()}",
        "",
        "## Launch Operations Documents",
        "",
    ]
    for doc in documents.get("documents", []):
        lines.append(f"- `{doc.get('path')}` — exists: {str(doc.get('exists')).lower()}")
    lines.extend([
        "",
        "## Phase 17 Verification",
        "",
        f"- Verifier: `{phase17.get('script')}`",
        f"- Return code: {phase17.get('returncode')}",
        f"- Valid: {str(phase17.get('valid')).lower()}",
        "",
        "This evidence records launch-governance readiness only. It does not authorise launch activation or live learner traffic.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_sha256sums(evidence_dir: pathlib.Path) -> pathlib.Path:
    sums_path = evidence_dir / "SHA256SUMS.txt"
    lines: list[str] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path != sums_path:
            lines.append(f"{sha256_file(path)}  {path.as_posix()}\n")
    sums_path.write_text("".join(lines), encoding="utf-8")
    return sums_path


def capture(args: argparse.Namespace) -> dict[str, Any]:
    claimed = bool(args.claim_controlled_beta_launch_governance)
    git_state = collect_git_state(args.target_branch)
    phase17 = run_phase17_verifier()
    documents = validate_operation_docs()
    result = build_result(claimed=claimed, phase17=phase17, git_state=git_state, documents=documents)

    record = {
        "schema_version": 1,
        "slice": "PHASE-18-CONTROLLED-BETA-LAUNCH-GOVERNANCE-AUTHORITY",
        "status": "controlled_beta_launch_governance_recorded" if result["valid"] else "controlled_beta_launch_governance_pending",
        "beta_scope": "controlled_beta_launch_governance_gate",
        "controlled_beta_launch_governance_claimed": claimed,
        "controlled_beta_launch_governance_recorded": result["valid"],
        "governance_owner": args.governance_owner,
        "captured_at": utc_now(),
        "target_branch": args.target_branch,
        "source_commit": git_state.get("head_sha"),
        "remote_target_sha": git_state.get("remote_target_sha"),
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": (EVIDENCE_DIR / "evidence_index.md").as_posix(),
        "sha256sums": (EVIDENCE_DIR / "SHA256SUMS.txt").as_posix(),
        "phase_17_controlled_beta_readiness_valid": result["phase_17_controlled_beta_readiness_valid"],
        "launch_operations_documents_valid": result["launch_operations_documents_valid"],
        **boundary_payload(),
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    raw_dir = EVIDENCE_DIR / "raw"
    write_json(raw_dir / "git_state.json", git_state)
    write_json(raw_dir / "phase17_controlled_beta_readiness_verification.json", phase17)
    write_json(raw_dir / "launch_operations_documents.json", documents)
    write_json(raw_dir / "launch_governance_boundary.json", boundary_payload())
    write_json(raw_dir / "controlled_beta_launch_governance_result.json", result)
    write_json(raw_dir / "controlled_beta_launch_governance_record_snapshot.json", record)
    write_evidence_index(EVIDENCE_DIR / "evidence_index.md", record, result, phase17, documents)
    sums = write_sha256sums(EVIDENCE_DIR)
    record["sha256sums"] = sums.as_posix()
    write_json(RECORD_PATH, record)
    write_json(raw_dir / "controlled_beta_launch_governance_record_snapshot.json", record)
    write_sha256sums(EVIDENCE_DIR)

    output = {**result, "record": RECORD_PATH.as_posix(), "evidence_dir": EVIDENCE_DIR.as_posix()}
    if args.require_valid and not output["valid"]:
        raise SystemExit(json.dumps(output, indent=2, sort_keys=True))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-controlled-beta-launch-governance", action="store_true")
    parser.add_argument("--governance-owner", default="")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.claim_controlled_beta_launch_governance and not args.governance_owner.strip():
        raise SystemExit("--governance-owner is required when claiming launch governance")
    result = capture(args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid:", result["valid"])
        for error in result["errors"]:
            print("ERROR:", error)
        for warning in result["warnings"]:
            print("WARNING:", warning)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
