#!/usr/bin/env python3
"""Capture Phase 17 controlled beta-readiness evidence.

This gate aggregates already-recorded authorities from the technical-audit and
runtime-readiness streams. It does not rerun heavyweight E2E tests and it does
not authorise production release, deployment, release tagging, public beta,
live learner traffic, learner data migration, or runtime KG implementation.
"""

from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import hashlib
import json
import pathlib
from scripts._subprocess import run
import sys
from datetime import datetime, timezone
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_17_controlled_beta_readiness_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/runtime-readiness/phase-17-controlled-beta-readiness")

VERIFIERS: tuple[tuple[str, str], ...] = (
    ("technical_audit_closure", "scripts/technical_audit/verify_technical_audit_closure.py"),
    ("post_merge_baseline", "scripts/technical_audit/verify_post_merge_baseline.py"),
    ("live_stack_readiness", "scripts/runtime_readiness/verify_live_stack_readiness.py"),
    ("backend_backed_e2e", "scripts/runtime_readiness/verify_backend_backed_e2e.py"),
    ("backend_backed_seeded_e2e", "scripts/runtime_readiness/verify_backend_backed_seeded_e2e.py"),
)

READINESS_DOCUMENTS: tuple[str, ...] = (
    "README.md",
    "PRIVACY_NOTICE.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "docs/roadmap/execution/runtime_readiness/14_live_stack_readiness_authority.md",
    "docs/roadmap/execution/runtime_readiness/15_backend_backed_e2e_authority.md",
    "docs/roadmap/execution/runtime_readiness/16_backend_backed_seeded_e2e_authority.md",
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


def run(cmd: list[str]) -> dict[str, Any]:
    proc = run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def git_value(args: list[str]) -> str | None:
    proc = run(["git", *args])
    if proc["returncode"] != 0:
        return None
    return str(proc["stdout"]).strip()


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256sums(evidence_dir: pathlib.Path) -> pathlib.Path:
    sums_path = evidence_dir / "SHA256SUMS.txt"
    entries: list[tuple[str, str]] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path.name != sums_path.name:
            entries.append((sha256_file(path), path.as_posix()))
    sums_path.write_text("".join(f"{digest}  {rel}\n" for digest, rel in entries), encoding="utf-8")
    return sums_path


def collect_verifier(name: str, script: str) -> dict[str, Any]:
    if not pathlib.Path(script).exists():
        return {
            "name": name,
            "script": script,
            "returncode": 127,
            "valid": False,
            "payload": {},
            "stderr": f"verifier missing: {script}",
        }
    proc = run([sys.executable, script, "--json"])
    try:
        parsed = json.loads(proc["stdout"] or "{}")
    except json.JSONDecodeError:
        parsed = {"raw_stdout": proc["stdout"]}
    return {
        "name": name,
        "script": script,
        "returncode": proc["returncode"],
        "valid": bool(isinstance(parsed, dict) and parsed.get("valid") is True and proc["returncode"] == 0),
        "payload": parsed,
        "stderr": proc["stderr"],
    }


def collect_git_state(target_branch: str) -> dict[str, Any]:
    head_sha = git_value(["rev-parse", "HEAD"])
    branch = git_value(["branch", "--show-current"])
    tracked_status = git_value(["status", "--short", "--untracked-files=no"])
    untracked_status = git_value(["status", "--short", "--untracked-files=all"])
    remote_sha = git_value(["rev-parse", f"origin/{target_branch}"])
    if remote_sha is None:
        remote_sha = git_value(["ls-remote", "origin", f"refs/heads/{target_branch}"])
    remote_target_sha = remote_sha.split()[0] if remote_sha else None
    return {
        "branch": branch,
        "head_sha": head_sha,
        "target_branch": target_branch,
        "remote_target_sha": remote_target_sha,
        "tracked_status": tracked_status or "",
        "full_status": untracked_status or "",
        "tracked_worktree_clean_before_capture": (tracked_status or "") == "",
        "head_matches_remote_target": bool(head_sha and remote_target_sha and head_sha == remote_target_sha),
    }


def collect_readiness_documents() -> dict[str, Any]:
    documents: list[dict[str, Any]] = []
    missing: list[str] = []
    for rel in READINESS_DOCUMENTS:
        path = pathlib.Path(rel)
        item: dict[str, Any] = {"path": rel, "exists": path.exists()}
        if path.exists() and path.is_file():
            item["sha256"] = sha256_file(path)
            item["size_bytes"] = path.stat().st_size
        else:
            missing.append(rel)
        documents.append(item)
    return {"documents": documents, "missing": missing, "valid": len(missing) == 0}


def boundary_payload() -> dict[str, Any]:
    return {
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "controlled_beta_launch_authorised": False,
        "live_learner_traffic_authorised": False,
        "learner_data_migration_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "scope": "controlled_beta_readiness_gate_only",
        "notes": [
            "Phase 17 aggregates readiness evidence only.",
            "A later explicit beta launch gate is required before live learner traffic or deployment.",
            "Runtime KG implementation remains out of scope.",
        ],
    }


def build_result(verifier_results: dict[str, dict[str, Any]], git_state: dict[str, Any], documents: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for name, result in verifier_results.items():
        if result.get("valid") is not True:
            errors.append(f"required verifier is not valid: {name}")
    if git_state.get("tracked_worktree_clean_before_capture") is not True:
        errors.append("tracked worktree must be clean before controlled beta readiness capture")
    if git_state.get("head_matches_remote_target") is not True:
        warnings.append("HEAD does not match origin target branch; record will remain reviewable but not ideal for final master evidence")
    if documents.get("valid") is not True:
        errors.append(f"required readiness documents missing: {documents.get('missing')}")
    return {
        "valid": len(errors) == 0,
        "controlled_beta_readiness_recorded": len(errors) == 0,
        "technical_audit_closure_valid": verifier_results.get("technical_audit_closure", {}).get("valid") is True,
        "post_merge_baseline_valid": verifier_results.get("post_merge_baseline", {}).get("valid") is True,
        "live_stack_readiness_valid": verifier_results.get("live_stack_readiness", {}).get("valid") is True,
        "backend_backed_e2e_valid": verifier_results.get("backend_backed_e2e", {}).get("valid") is True,
        "seeded_backend_backed_e2e_valid": verifier_results.get("backend_backed_seeded_e2e", {}).get("valid") is True,
        "readiness_documents_valid": documents.get("valid") is True,
        "errors": errors,
        "warnings": warnings,
        **boundary_payload(),
    }


def write_evidence_index(path: pathlib.Path, record: dict[str, Any], result: dict[str, Any], verifier_results: dict[str, dict[str, Any]]) -> None:
    lines = [
        "# Phase 17 Controlled Beta Readiness Evidence",
        "",
        f"Captured at: {record['captured_at']}",
        f"Readiness owner: {record['readiness_owner']}",
        f"Source commit: {record['source_commit']}",
        f"Target branch: {record['target_branch']}",
        "",
        "## Readiness Inputs",
        "",
        f"- Technical audit closure valid: {str(result['technical_audit_closure_valid']).lower()}",
        f"- Post-merge baseline valid: {str(result['post_merge_baseline_valid']).lower()}",
        f"- Live-stack readiness valid: {str(result['live_stack_readiness_valid']).lower()}",
        f"- Backend-backed E2E valid: {str(result['backend_backed_e2e_valid']).lower()}",
        f"- Seeded backend-backed E2E valid: {str(result['seeded_backend_backed_e2e_valid']).lower()}",
        f"- Readiness documents valid: {str(result['readiness_documents_valid']).lower()}",
        "",
        "## Boundary",
        "",
        "- Controlled beta readiness recorded: true",
        "- Production release authorised: false",
        "- Deployment authorised: false",
        "- Release tag authorised: false",
        "- Public beta authorised: false",
        "- Controlled beta launch authorised: false",
        "- Live learner traffic authorised: false",
        "- Learner data migration authorised: false",
        "- Runtime KG implementation claimed: false",
        "",
        "## Verifiers",
        "",
    ]
    for name, verifier in verifier_results.items():
        lines.append(f"- {name}: valid={str(verifier.get('valid') is True).lower()} script=`{verifier.get('script')}`")
    lines.extend(["", "## Result", "", f"Valid: {str(result['valid']).lower()}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--claim-controlled-beta-readiness", action="store_true")
    parser.add_argument("--readiness-owner", default="")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    raw_dir = EVIDENCE_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    verifier_results = {name: collect_verifier(name, script) for name, script in VERIFIERS}
    git_state = collect_git_state(args.target_branch)
    documents = collect_readiness_documents()
    boundary = boundary_payload()
    result = build_result(verifier_results, git_state, documents)

    if not args.claim_controlled_beta_readiness:
        result["valid"] = False
        result["controlled_beta_readiness_recorded"] = False
        result.setdefault("errors", []).append("--claim-controlled-beta-readiness is required")
    if not args.readiness_owner.strip():
        result["valid"] = False
        result["controlled_beta_readiness_recorded"] = False
        result.setdefault("errors", []).append("--readiness-owner is required")

    write_json(raw_dir / "git_state.json", git_state)
    write_json(raw_dir / "readiness_documents.json", documents)
    write_json(raw_dir / "beta_boundary.json", boundary)
    for name, verifier in verifier_results.items():
        write_json(raw_dir / f"{name}_verification.json", verifier)
    write_json(raw_dir / "controlled_beta_readiness_result.json", result)

    record = {
        "schema_version": 1,
        "slice": "PHASE-17-CONTROLLED-BETA-READINESS-AUTHORITY",
        "status": "controlled_beta_readiness_recorded" if result["valid"] else "controlled_beta_readiness_capture_invalid",
        "controlled_beta_readiness_claimed": bool(args.claim_controlled_beta_readiness),
        "controlled_beta_readiness_recorded": bool(result["valid"]),
        "beta_scope": "controlled_beta_readiness_gate",
        "readiness_owner": args.readiness_owner.strip(),
        "captured_at": utc_now(),
        "target_branch": args.target_branch,
        "source_commit": git_state.get("head_sha"),
        "remote_target_sha": git_state.get("remote_target_sha"),
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": (EVIDENCE_DIR / "evidence_index.md").as_posix(),
        "sha256sums": (EVIDENCE_DIR / "SHA256SUMS.txt").as_posix(),
        "technical_audit_closure_valid": result["technical_audit_closure_valid"],
        "post_merge_baseline_valid": result["post_merge_baseline_valid"],
        "live_stack_readiness_valid": result["live_stack_readiness_valid"],
        "backend_backed_e2e_valid": result["backend_backed_e2e_valid"],
        "seeded_backend_backed_e2e_valid": result["seeded_backend_backed_e2e_valid"],
        "readiness_documents_valid": result["readiness_documents_valid"],
        **boundary,
    }

    write_evidence_index(EVIDENCE_DIR / "evidence_index.md", record, result, verifier_results)
    sums_path = write_sha256sums(EVIDENCE_DIR)
    record["sha256sums"] = sums_path.as_posix()
    write_json(RECORD_PATH, record)
    write_json(raw_dir / "controlled_beta_readiness_record_snapshot.json", record)
    # Recompute sums after adding record snapshot.
    sums_path = write_sha256sums(EVIDENCE_DIR)
    record["sha256sums"] = sums_path.as_posix()
    write_json(RECORD_PATH, record)

    output = {"valid": result["valid"], "record": RECORD_PATH.as_posix(), "evidence_dir": EVIDENCE_DIR.as_posix(), **result}
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print("valid:", output["valid"])
        for error in output.get("errors", []):
            print("ERROR:", error)
        for warning in output.get("warnings", []):
            print("WARNING:", warning)
    if args.require_valid and not output["valid"]:
        return 1
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
