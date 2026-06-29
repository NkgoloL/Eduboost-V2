#!/usr/bin/env python3
"""Capture TA Phase 13B post-merge protected-branch baseline evidence.

Run this from the protected base branch after Phase 13A and this Phase 13B
harness have landed. It records a post-merge baseline only; it does not
authorise production release or deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

REGISTER_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")
RECORD_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/technical_audit_post_merge_baseline_record.json")
HOSTED_RECORD_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/technical-audit/phase-13b-post-merge-baseline")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def git_value(args: list[str]) -> str | None:
    proc = run(["git", *args])
    if proc["returncode"] != 0:
        return None
    return str(proc["stdout"]).strip()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_verifier(script: str) -> dict[str, Any]:
    proc = run([sys.executable, script, "--json"])
    try:
        parsed = json.loads(proc["stdout"] or "{}")
    except json.JSONDecodeError:
        parsed = {"raw_stdout": proc["stdout"]}
    return {
        "script": script,
        "returncode": proc["returncode"],
        "valid": bool(isinstance(parsed, dict) and parsed.get("valid") is True and proc["returncode"] == 0),
        "payload": parsed,
        "stderr": proc["stderr"],
    }


def gh_json(args: list[str]) -> dict[str, Any]:
    proc = run(["gh", *args])
    if proc["returncode"] != 0:
        return {"ok": False, "returncode": proc["returncode"], "stdout": proc["stdout"], "stderr": proc["stderr"]}
    try:
        payload = json.loads(proc["stdout"] or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "returncode": 0, "stdout": proc["stdout"], "stderr": "invalid JSON"}
    if isinstance(payload, dict):
        payload["ok"] = True
        return payload
    return {"ok": True, "payload": payload}


def write_sha256sums(evidence_dir: pathlib.Path) -> pathlib.Path:
    sums_path = evidence_dir / "SHA256SUMS.txt"
    entries: list[tuple[str, str]] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path.name != sums_path.name:
            entries.append((sha256_file(path), path.as_posix()))
    sums_path.write_text("".join(f"{digest}  {rel}\n" for digest, rel in entries), encoding="utf-8")
    return sums_path


def check_required_check_configured(protection_payload: dict[str, Any], required_check: str) -> bool:
    status_checks = protection_payload.get("required_status_checks") or {}
    contexts = status_checks.get("contexts") or []
    checks = status_checks.get("checks") or []
    check_contexts = {item for item in contexts if isinstance(item, str)}
    for item in checks:
        if isinstance(item, dict):
            if isinstance(item.get("context"), str):
                check_contexts.add(item["context"])
            if isinstance(item.get("name"), str):
                check_contexts.add(item["name"])
    return required_check in check_contexts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub repository, for example NkgoloL/Eduboost-V2")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--required-check", default="Verify repository authority")
    parser.add_argument("--claim-post-merge-baseline", action="store_true")
    parser.add_argument("--baseline-owner", default="")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    branch = git_value(["branch", "--show-current"])
    head_sha = git_value(["rev-parse", "HEAD"])
    remote_sha = git_value(["rev-parse", f"origin/{args.target_branch}"])
    tracked_status = run(["git", "status", "--porcelain", "--untracked-files=no"])
    untracked_status = run(["git", "status", "--porcelain", "--untracked-files=normal"])
    git_state = {
        "branch": branch,
        "head_sha": head_sha,
        "target_branch": args.target_branch,
        "remote_target_sha": remote_sha,
        "tracked_worktree_clean_before_capture": tracked_status["stdout"].strip() == "",
        "tracked_status_before_capture": tracked_status["stdout"].splitlines(),
        "status_before_capture_including_untracked": untracked_status["stdout"].splitlines(),
    }

    if branch != args.target_branch:
        errors.append(f"post-merge baseline must be captured from {args.target_branch}; current branch is {branch}")
    if not head_sha:
        errors.append("could not resolve HEAD")
    if remote_sha and head_sha and remote_sha != head_sha:
        errors.append(f"HEAD must match origin/{args.target_branch}; HEAD={head_sha}, origin/{args.target_branch}={remote_sha}")
    if tracked_status["stdout"].strip():
        errors.append("tracked worktree must be clean before post-merge baseline capture")
    if args.claim_post_merge_baseline and not args.baseline_owner.strip():
        errors.append("--baseline-owner is required when claiming post-merge baseline")

    verifiers = {
        "hosted_ci_authority": collect_verifier("scripts/technical_audit/verify_hosted_ci_authority.py"),
        "merge_readiness": collect_verifier("scripts/technical_audit/verify_merge_readiness_authority.py"),
        "release_readiness": collect_verifier("scripts/technical_audit/verify_release_readiness_authority.py"),
        "technical_audit_closure": collect_verifier("scripts/technical_audit/verify_technical_audit_closure.py"),
    }
    for name, payload in verifiers.items():
        if payload.get("valid") is not True:
            errors.append(f"{name} verifier must be valid before post-merge baseline capture")

    blocker_register = load_json(REGISTER_PATH) if REGISTER_PATH.exists() else {}
    hosted_record = load_json(HOSTED_RECORD_PATH) if HOSTED_RECORD_PATH.exists() else {}

    if blocker_register.get("status") not in {
        "phase_12_technical_audit_remediation_closed",
        "phase_13b_post_merge_baseline_authority_ready",
        "phase_13b_post_merge_baseline_recorded",
    }:
        errors.append("blocker_register.status must show closed technical-audit remediation or Phase 13B baseline state")
    if blocker_register.get("active_slice") not in {
        "technical-audit-remediation-closed",
        "technical-audit-post-merge-baseline-authority",
        "technical-audit-post-merge-baseline-recorded",
    }:
        errors.append("blocker_register.active_slice is not a recognised terminal/post-merge state")

    split_fields = ["ci_run_sha", "evidence_commit_sha", "closure_commit_sha", "current_terminal_sha"]
    missing_split = [field for field in split_fields if not hosted_record.get(field)]
    if missing_split:
        errors.append(f"hosted CI authority record is missing split provenance fields: {', '.join(missing_split)}")

    branch_payload = gh_json(["api", f"repos/{args.repo}/branches/{args.target_branch}"])
    protection_payload = gh_json(["api", f"repos/{args.repo}/branches/{args.target_branch}/protection"])
    check_runs_payload = gh_json(["api", f"repos/{args.repo}/commits/{head_sha}/check-runs"]) if head_sha else {"ok": False}

    if branch_payload.get("ok") is not True:
        errors.append("could not read GitHub target branch state with gh api")
    elif branch_payload.get("commit", {}).get("sha") != head_sha:
        errors.append("GitHub target branch SHA does not match local HEAD")

    if protection_payload.get("ok") is not True:
        errors.append("could not read GitHub branch protection state with gh api")
    else:
        status_checks = protection_payload.get("required_status_checks") or {}
        if status_checks.get("strict") is not True:
            errors.append("branch protection required_status_checks.strict must be true")
        if not check_required_check_configured(protection_payload, args.required_check):
            errors.append(f"required check is not configured in branch protection: {args.required_check}")
        if (protection_payload.get("allow_force_pushes") or {}).get("enabled") is not False:
            errors.append("branch protection must not allow force pushes")
        if (protection_payload.get("allow_deletions") or {}).get("enabled") is not False:
            errors.append("branch protection must not allow deletions")

    required_check_seen = False
    required_check_success = False
    if check_runs_payload.get("ok") is True:
        for check in check_runs_payload.get("check_runs", []) or []:
            if check.get("name") == args.required_check:
                required_check_seen = True
                required_check_success = check.get("status") == "completed" and check.get("conclusion") == "success"
                break
    if not required_check_seen:
        errors.append(f"required check run not found on current HEAD: {args.required_check}")
    elif not required_check_success:
        errors.append(f"required check run is not successful on current HEAD: {args.required_check}")

    valid_preclaim = len(errors) == 0
    claimed = bool(args.claim_post_merge_baseline and valid_preclaim)
    result = {
        "valid": bool(valid_preclaim and (claimed or not args.require_valid)),
        "post_merge_baseline_claimed": claimed,
        "post_merge_baseline_recorded": claimed,
        "repository": args.repo,
        "branch": branch,
        "target_branch": args.target_branch,
        "head_sha": head_sha,
        "remote_target_sha": remote_sha,
        "required_check": args.required_check,
        "technical_audit_remediation_closed": verifiers["technical_audit_closure"].get("valid") is True,
        "hosted_ci_authority_valid": verifiers["hosted_ci_authority"].get("valid") is True,
        "merge_readiness_authorised": verifiers["merge_readiness"].get("valid") is True,
        "technical_audit_release_readiness_claimed": verifiers["release_readiness"].get("valid") is True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "errors": errors,
        "warnings": warnings,
    }

    if args.claim_post_merge_baseline and not valid_preclaim:
        result["valid"] = False
    if args.require_valid and not result["valid"]:
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("valid:", result["valid"])
            for error in errors:
                print("error:", error, file=sys.stderr)
        return 1

    if claimed:
        now = utc_now()
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        raw = EVIDENCE_DIR / "raw"
        raw.mkdir(parents=True, exist_ok=True)

        write_json(raw / "git_state.json", git_state)
        write_json(raw / "blocker_register_snapshot.json", blocker_register)
        write_json(raw / "hosted_ci_authority_record_snapshot.json", hosted_record)
        write_json(raw / "hosted_ci_authority_verification.json", verifiers["hosted_ci_authority"])
        write_json(raw / "merge_readiness_verification.json", verifiers["merge_readiness"])
        write_json(raw / "release_readiness_verification.json", verifiers["release_readiness"])
        write_json(raw / "technical_audit_closure_verification.json", verifiers["technical_audit_closure"])
        write_json(raw / "github_branch_state.json", branch_payload)
        write_json(raw / "github_branch_protection.json", protection_payload)
        write_json(raw / "github_check_runs.json", check_runs_payload)
        write_json(raw / "post_merge_baseline_result.json", result)

        index_path = EVIDENCE_DIR / "evidence_index.md"
        index_text = f"""# TA Phase 13B Post-Merge Protected-Branch Baseline Evidence

Captured at: {now}
Repository: `{args.repo}`
Target branch: `{args.target_branch}`
Source commit: `{head_sha}`
Required check: `{args.required_check}`

Decision: Post-merge protected-branch technical-audit baseline recorded.
Technical-audit remediation closed: true
Hosted CI authority valid: true
Merge readiness authorised: true
Technical-audit release readiness claimed: true
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Live learner traffic authorised: false
Runtime KG implementation claimed: false

This evidence records the protected-branch baseline only. It does not authorise
production release, deployment, release tagging, live learner traffic, or runtime
knowledge-graph implementation.
"""
        index_path.write_text(index_text, encoding="utf-8")
        index_sha_path = EVIDENCE_DIR / "evidence_index.sha256"
        index_sha_path.write_text(sha256_file(index_path) + "  " + index_path.as_posix() + "\n", encoding="utf-8")
        sums_path = write_sha256sums(EVIDENCE_DIR)

        record = {
            "schema_version": 1,
            "slice": "TA-PHASE-13B-POST-MERGE-PROTECTED-BRANCH-BASELINE",
            "status": "post_merge_protected_branch_baseline_recorded",
            "repository": args.repo,
            "branch": branch,
            "target_branch": args.target_branch,
            "required_check": args.required_check,
            "baseline_owner": args.baseline_owner.strip(),
            "claimed_at_utc": now,
            "updated_at_utc": now,
            "source_commit": head_sha,
            "remote_target_sha": remote_sha,
            "post_merge_baseline_claimed": True,
            "post_merge_baseline_recorded": True,
            "technical_audit_remediation_closed": True,
            "hosted_ci_authority_valid": True,
            "merge_readiness_authorised": True,
            "technical_audit_release_readiness_claimed": True,
            "hosted_ci_provenance_model": "split_ci_run_evidence_closure_terminal_sha",
            "ci_run_sha": hosted_record.get("ci_run_sha"),
            "evidence_commit_sha": hosted_record.get("evidence_commit_sha"),
            "closure_commit_sha": hosted_record.get("closure_commit_sha"),
            "current_terminal_sha": hosted_record.get("current_terminal_sha"),
            "post_merge_baseline_sha": head_sha,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "live_learner_traffic_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "full_backend_backed_e2e_claimed": False,
            "evidence_dir": EVIDENCE_DIR.as_posix(),
            "evidence_index": index_path.as_posix(),
            "sha256sums": sums_path.as_posix(),
        }
        write_json(RECORD_PATH, record)

        register = blocker_register if isinstance(blocker_register, dict) else {}
        register["active_slice"] = "technical-audit-post-merge-baseline-recorded"
        register["status"] = "phase_13b_post_merge_baseline_recorded"
        register["phase_13b_post_merge_baseline_authority"] = {
            "id": "TA-POST-MERGE-BASELINE-001",
            "title": "Post-merge protected-branch baseline authority",
            "status": "post_merge_baseline_recorded",
            "authority_record": RECORD_PATH.as_posix(),
            "evidence_path": EVIDENCE_DIR.as_posix(),
            "target_branch": args.target_branch,
            "required_check": args.required_check,
            "source_commit": head_sha,
            "post_merge_baseline_recorded": True,
            "technical_audit_remediation_closed": True,
            "hosted_ci_authority_valid": True,
            "merge_readiness_authorised": True,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "live_learner_traffic_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "updated_at_utc": now,
        }
        write_json(REGISTER_PATH, register)
        result.update({"record": RECORD_PATH.as_posix(), "evidence_dir": EVIDENCE_DIR.as_posix(), "sha256sums": sums_path.as_posix()})

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid:", result["valid"])
        for warning in warnings:
            print("warning:", warning)
        for error in errors:
            print("error:", error, file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
