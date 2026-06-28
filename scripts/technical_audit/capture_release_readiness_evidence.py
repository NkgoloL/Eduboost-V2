#!/usr/bin/env python3
"""Capture technical-audit release-readiness evidence.

This capture is fail-closed. It only records release readiness when explicitly
called with --claim-release-readiness and when all prerequisite authority records
are valid. The claim is scoped to the technical-audit remediation stream; it does
not authorise a production launch, deployment, release tag, or runtime KG pivot.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

REGISTER_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")
HOSTED_RECORD_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json")
RELEASE_RECORD_PATH = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/technical_audit_release_readiness_record.json"
)
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/technical-audit/phase-11-release-readiness")
RAW_DIR = EVIDENCE_DIR / "raw"
MERGE_VERIFIER = pathlib.Path("scripts/technical_audit/verify_merge_readiness_authority.py")

REQUIRED_BLOCKERS = [
    "TA-OPENAPI-001",
    "TA-BACKEND-FAST-001",
    "TA-FRONTEND-001",
    "TA-E2E-001",
    "TA-SECURITY-001",
    "TA-CI-001",
    "TA-REMOTE-CI-001",
    "TA-HOSTED-CI-001",
]
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_value(args: list[str], default: str | None = None) -> str | None:
    try:
        return run(["git", *args]).stdout.strip()
    except Exception:
        return default


def tracked_worktree_clean() -> bool:
    diff = subprocess.run(["git", "diff", "--quiet"], text=True)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], text=True)
    return diff.returncode == 0 and staged.returncode == 0


def untracked_files() -> list[str]:
    try:
        out = run(["git", "ls-files", "--others", "--exclude-standard"]).stdout
    except Exception:
        return []
    return [line for line in out.splitlines() if line.strip()]


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON file: {path}: {exc}") from exc


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256sums(files: list[pathlib.Path], sums_path: pathlib.Path) -> None:
    unique = sorted({p for p in files if p.exists()}, key=lambda p: p.as_posix())
    lines = [f"{sha256_file(path)}  {path.as_posix()}" for path in unique]
    sums_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def run_merge_verifier() -> dict[str, Any]:
    if not MERGE_VERIFIER.exists():
        return {
            "valid": False,
            "errors": [f"missing merge-readiness verifier: {MERGE_VERIFIER}"],
            "warnings": [],
            "checked": [],
        }
    completed = run([sys.executable, str(MERGE_VERIFIER), "--json"], check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "valid": False,
            "errors": ["merge verifier did not return JSON"],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    payload.setdefault("command", f"{sys.executable} {MERGE_VERIFIER} --json")
    payload.setdefault("returncode", completed.returncode)
    return payload


def _find_blocker(register: dict[str, Any], blocker_id: str) -> dict[str, Any] | None:
    blockers = register.get("remaining_release_blockers_after_reset")
    if not isinstance(blockers, list):
        return None
    for item in blockers:
        if isinstance(item, dict) and item.get("id") == blocker_id:
            return item
    return None


def build_blocker_summary(register: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    for blocker_id in REQUIRED_BLOCKERS:
        item = _find_blocker(register, blocker_id)
        if item is None:
            checks[blocker_id] = {"valid": False, "error": "missing_from_remaining_release_blockers_after_reset"}
            continue
        valid = item.get("status") == "evidence_recorded"
        extra_errors: list[str] = []
        if blocker_id == "TA-HOSTED-CI-001":
            if item.get("remote_ci_run_claimed") is not True:
                extra_errors.append("remote_ci_run_claimed must be true")
            if item.get("branch_protection_claimed") is not True:
                extra_errors.append("branch_protection_claimed must be true")
            if item.get("merge_readiness_authorised") is not True:
                extra_errors.append("merge_readiness_authorised must be true")
        checks[blocker_id] = {
            "valid": valid and not extra_errors,
            "status": item.get("status"),
            "latest_valid_evidence_commit": item.get("latest_valid_evidence_commit"),
            "errors": extra_errors,
        }
    failed = [key for key, value in checks.items() if not value.get("valid")]
    return {
        "schema_version": 1,
        "required_blockers": REQUIRED_BLOCKERS,
        "checks": checks,
        "required_blockers_closed": not failed,
        "failed_blockers": failed,
    }


def evaluate_release_readiness(
    *,
    claim: bool,
    release_owner: str | None,
    source_commit: str | None,
    tracked_clean: bool,
    merge_result: dict[str, Any],
    hosted_record: dict[str, Any],
    blocker_summary: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not claim:
        errors.append("release readiness is not claimed; rerun with --claim-release-readiness to close this phase")
    if not release_owner or not release_owner.strip():
        errors.append("release_owner is required")
    if not source_commit or not SHA_RE.match(source_commit):
        errors.append("source_commit must be a 40-character lowercase git SHA")
    if tracked_clean is not True:
        errors.append("tracked worktree must be clean before release-readiness capture")

    if merge_result.get("valid") is not True:
        errors.append("merge-readiness verifier must be valid")
    if merge_result.get("hosted_ci_run_claimed") is not True:
        errors.append("merge-readiness verifier must report hosted_ci_run_claimed=true")
    if merge_result.get("branch_protection_claimed") is not True:
        errors.append("merge-readiness verifier must report branch_protection_claimed=true")
    if merge_result.get("merge_readiness_authorised") is not True:
        errors.append("merge-readiness verifier must report merge_readiness_authorised=true")

    if hosted_record.get("hosted_ci_run_claimed") is not True:
        errors.append("hosted authority record must claim hosted CI run")
    if hosted_record.get("hosted_ci_conclusion") != "success":
        errors.append("hosted authority record hosted_ci_conclusion must be success")
    if hosted_record.get("branch_protection_claimed") is not True:
        errors.append("hosted authority record must claim branch protection")
    if hosted_record.get("merge_readiness_authorised") is not True:
        errors.append("hosted authority record must authorise merge readiness")
    if hosted_record.get("head_sha") != source_commit:
        errors.append("hosted authority record head_sha must match current branch HEAD")

    if blocker_summary.get("required_blockers_closed") is not True:
        errors.append(f"required blockers are not all closed: {blocker_summary.get('failed_blockers')}")

    if hosted_record.get("runtime_kg_implementation_claimed") is True:
        errors.append("runtime KG implementation must not be claimed by this release-readiness gate")
    if hosted_record.get("production_release_authorised") is True:
        errors.append("production release must not be authorised by this technical-audit gate")

    valid = not errors
    return {
        "schema_version": 1,
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "release_readiness_claimed": bool(claim and valid),
        "technical_audit_release_readiness_claimed": bool(claim and valid),
        "production_release_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "source_commit": source_commit,
        "release_owner": release_owner.strip() if release_owner else None,
        "required_blockers_closed": blocker_summary.get("required_blockers_closed") is True,
        "hosted_ci_run_claimed": merge_result.get("hosted_ci_run_claimed") is True,
        "branch_protection_claimed": merge_result.get("branch_protection_claimed") is True,
        "merge_readiness_authorised": merge_result.get("merge_readiness_authorised") is True,
        "scope": "technical-audit remediation release-readiness only; not production launch",
    }


def write_evidence_index(result: dict[str, Any], git_state: dict[str, Any], evidence_files: list[pathlib.Path]) -> pathlib.Path:
    status = "Technical-audit release readiness authorised" if result.get("release_readiness_claimed") else "Technical-audit release readiness not claimed"
    lines = [
        "# TA Phase 11 — Technical-Audit Release Readiness Evidence",
        "",
        f"Status: {status}",
        f"Captured at UTC: {utc_now()}",
        f"Source commit: `{git_state.get('head_sha')}`",
        f"Branch: `{git_state.get('branch')}`",
        f"Release owner: `{result.get('release_owner') or 'unclaimed'}`",
        "",
        "## Claims",
        "",
        f"- Release readiness claimed: {str(result.get('release_readiness_claimed')).lower()}",
        f"- Hosted CI run claimed: {str(result.get('hosted_ci_run_claimed')).lower()}",
        f"- Branch protection claimed: {str(result.get('branch_protection_claimed')).lower()}",
        f"- Merge readiness authorised: {str(result.get('merge_readiness_authorised')).lower()}",
        f"- Production release authorised: {str(result.get('production_release_authorised')).lower()}",
        f"- Runtime KG implementation claimed: {str(result.get('runtime_kg_implementation_claimed')).lower()}",
        "",
        "## Evidence files",
        "",
    ]
    for path in evidence_files:
        lines.append(f"- `{path.as_posix()}`")
    lines.extend([
        "",
        "## Boundary",
        "",
        "This evidence closes only the technical-audit remediation release-readiness authority. It does not deploy the product, create a production release tag, authorise live learner traffic, change POPIA processing scope, or implement runtime knowledge graphs.",
        "",
    ])
    index = EVIDENCE_DIR / "evidence_index.md"
    index.write_text("\n".join(lines), encoding="utf-8")
    return index


def update_register(register: dict[str, Any], result: dict[str, Any], record_path: pathlib.Path, evidence_dir: pathlib.Path) -> dict[str, Any]:
    phase = register.setdefault("phase_11_release_readiness_authority", {})
    phase.update(
        {
            "id": "TA-RELEASE-READINESS-001",
            "title": "Technical-audit release-readiness authority",
            "status": "technical_audit_release_readiness_authorised" if result.get("release_readiness_claimed") else "release_readiness_unclaimed",
            "authority_record": record_path.as_posix(),
            "evidence_path": evidence_dir.as_posix(),
            "release_readiness_claimed": result.get("release_readiness_claimed") is True,
            "technical_audit_release_readiness_claimed": result.get("technical_audit_release_readiness_claimed") is True,
            "production_release_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "hosted_ci_run_claimed": result.get("hosted_ci_run_claimed") is True,
            "branch_protection_claimed": result.get("branch_protection_claimed") is True,
            "merge_readiness_authorised": result.get("merge_readiness_authorised") is True,
            "release_owner": result.get("release_owner"),
            "updated_at_utc": utc_now(),
        }
    )
    if result.get("release_readiness_claimed"):
        register["active_slice"] = "technical-audit-release-readiness-closed"
        register["status"] = "phase_11_technical_audit_release_readiness_closed"
    else:
        register["active_slice"] = "technical-audit-release-readiness-authority"
        register["status"] = "phase_11_release_readiness_authority_ready"
    return register


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-release-readiness", action="store_true", help="explicitly claim scoped technical-audit release readiness")
    parser.add_argument("--release-owner", help="name of the release owner making the claim")
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    parser.add_argument("--record", default=str(RELEASE_RECORD_PATH))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    global EVIDENCE_DIR, RAW_DIR
    EVIDENCE_DIR = pathlib.Path(args.evidence_dir)
    RAW_DIR = EVIDENCE_DIR / "raw"
    record_path = pathlib.Path(args.record)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    source_commit = git_value(["rev-parse", "HEAD"])
    branch = git_value(["branch", "--show-current"], default="unknown")
    tracked_clean = tracked_worktree_clean()
    untracked = untracked_files()

    git_state = {
        "schema_version": 1,
        "branch": branch,
        "head_sha": source_commit,
        "tracked_worktree_clean_before_capture": tracked_clean,
        "untracked_files_present": bool(untracked),
        "untracked_files_sample": untracked[:20],
        "captured_at_utc": utc_now(),
    }
    register = load_json(REGISTER_PATH)
    hosted_record = load_json(HOSTED_RECORD_PATH)
    merge_result = run_merge_verifier()
    blocker_summary = build_blocker_summary(register)
    result = evaluate_release_readiness(
        claim=args.claim_release_readiness,
        release_owner=args.release_owner,
        source_commit=source_commit,
        tracked_clean=tracked_clean,
        merge_result=merge_result,
        hosted_record=hosted_record,
        blocker_summary=blocker_summary,
    )

    raw_files: list[pathlib.Path] = []
    payloads = {
        RAW_DIR / "git_state.json": git_state,
        RAW_DIR / "blocker_register_snapshot.json": register,
        RAW_DIR / "hosted_ci_authority_record_snapshot.json": hosted_record,
        RAW_DIR / "merge_readiness_verification.json": merge_result,
        RAW_DIR / "required_blocker_summary.json": blocker_summary,
        RAW_DIR / "release_readiness_result.json": result,
    }
    for path, payload in payloads.items():
        write_json(path, payload)
        raw_files.append(path)

    index = write_evidence_index(result, git_state, raw_files)
    index_hash = EVIDENCE_DIR / "evidence_index.sha256"
    index_hash.write_text(f"{sha256_file(index)}  {index.as_posix()}\n", encoding="utf-8")
    sums = EVIDENCE_DIR / "SHA256SUMS.txt"
    write_sha256sums([*raw_files, index, index_hash], sums)

    record = {
        "schema_version": 1,
        "slice": "TA-PHASE-11-TECHNICAL-AUDIT-RELEASE-READINESS",
        "status": "technical_audit_release_readiness_authorised" if result.get("release_readiness_claimed") else "release_readiness_unclaimed",
        "repository": hosted_record.get("repository"),
        "branch": branch,
        "source_commit": source_commit,
        "release_owner": result.get("release_owner"),
        "release_decision": "authorised" if result.get("release_readiness_claimed") else "unclaimed",
        "claimed_at_utc": utc_now() if result.get("release_readiness_claimed") else None,
        "release_readiness_claimed": result.get("release_readiness_claimed") is True,
        "technical_audit_release_readiness_claimed": result.get("technical_audit_release_readiness_claimed") is True,
        "production_release_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "hosted_ci_run_claimed": result.get("hosted_ci_run_claimed") is True,
        "branch_protection_claimed": result.get("branch_protection_claimed") is True,
        "merge_readiness_authorised": result.get("merge_readiness_authorised") is True,
        "required_blockers_closed": result.get("required_blockers_closed") is True,
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": index.as_posix(),
        "sha256sums": sums.as_posix(),
        "constraints": [
            "Release readiness is scoped to the technical-audit remediation stream only.",
            "Production launch, release tagging, deployment, and live learner traffic remain out of scope.",
            "Runtime knowledge-graph implementation remains out of scope.",
            "The release-readiness claim requires explicit --claim-release-readiness and a release owner.",
        ],
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
    }
    write_json(record_path, record)
    updated_register = update_register(register, result, record_path, EVIDENCE_DIR)
    write_json(REGISTER_PATH, updated_register)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

