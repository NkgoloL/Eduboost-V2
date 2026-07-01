#!/usr/bin/env python3
"""Capture Phase 19 controlled beta activation-preflight evidence.

This is not a launch activation gate. It verifies Phase 18 launch-governance
readiness and the activation-preflight pack, then records that activation
preflight is reviewable while all launch, deployment, learner-migration, live
traffic, production release, and runtime KG boundaries remain false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
from datetime import datetime, timezone
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_19_controlled_beta_activation_preflight_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/runtime-readiness/phase-19-controlled-beta-activation-preflight")
PHASE18_VERIFY = pathlib.Path("scripts/runtime_readiness/verify_controlled_beta_launch_governance.py")
REQUIRED_PREFLIGHT_DOCS: tuple[pathlib.Path, ...] = (
    pathlib.Path("docs/operations/beta/controlled_beta_activation_preflight_checklist.md"),
    pathlib.Path("docs/operations/beta/controlled_beta_go_no_go_decision.template.md"),
    pathlib.Path("docs/operations/beta/controlled_beta_participant_onboarding_checklist.md"),
    pathlib.Path("docs/operations/beta/controlled_beta_traffic_control_plan.md"),
    pathlib.Path("docs/operations/beta/controlled_beta_data_migration_dry_run_checklist.md"),
    pathlib.Path("docs/operations/beta/controlled_beta_launch_activation_boundary.md"),
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


def run_command(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    payload: dict[str, Any] | None = None
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = None
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "valid": proc.returncode == 0 and (payload or {}).get("valid") is True,
        "payload": payload,
    }


def git_state(target_branch: str) -> dict[str, Any]:
    head = subprocess.run(["git", "rev-parse", "HEAD"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout.strip()
    branch = subprocess.run(["git", "branch", "--show-current"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout.strip()
    status = subprocess.run(["git", "status", "--short"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    remote = subprocess.run(["git", "rev-parse", f"origin/{target_branch}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    remote_sha = remote.stdout.strip() if remote.returncode == 0 else ""
    return {
        "branch": branch,
        "head_sha": head,
        "target_branch": target_branch,
        "remote_target_sha": remote_sha,
        "head_matches_remote_target": bool(head and remote_sha and head == remote_sha),
        "git_status_short": status.stdout.splitlines(),
        "tracked_worktree_clean_before_capture": status.stdout.strip() == "",
    }


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
        "scope": "controlled_beta_activation_preflight_only",
    }


def validate_preflight_documents() -> dict[str, Any]:
    errors: list[str] = []
    documents: list[dict[str, Any]] = []
    required_markers = (
        "does not authorise controlled beta launch",
        "live learner traffic authorised: false",
    )
    for doc in REQUIRED_PREFLIGHT_DOCS:
        item: dict[str, Any] = {"path": doc.as_posix(), "exists": doc.exists()}
        if not doc.exists():
            errors.append(f"missing preflight document: {doc}")
            documents.append(item)
            continue
        text = doc.read_text(encoding="utf-8")
        item.update({"sha256": sha256_file(doc), "bytes": doc.stat().st_size})
        for marker in required_markers:
            if marker not in text.lower():
                errors.append(f"{doc} missing marker: {marker}")
        documents.append(item)
    return {"valid": not errors, "documents": documents, "errors": errors}


def build_result(*, claimed: bool, phase18: dict[str, Any], git: dict[str, Any], documents: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not claimed:
        errors.append("controlled beta activation preflight was not claimed")
    if phase18.get("valid") is not True:
        errors.append("Phase 18 controlled beta launch-governance verifier is not valid")
    if git.get("tracked_worktree_clean_before_capture") is not True:
        errors.append("tracked worktree must be clean before activation-preflight capture")
    if git.get("head_matches_remote_target") is not True:
        errors.append("HEAD must match origin target branch before activation-preflight capture")
    if documents.get("valid") is not True:
        errors.extend(documents.get("errors") or ["activation preflight documents are invalid"])
    return {
        "valid": not errors,
        "controlled_beta_activation_preflight_claimed": claimed,
        "controlled_beta_activation_preflight_recorded": not errors,
        "phase_18_controlled_beta_launch_governance_valid": phase18.get("valid") is True,
        "activation_preflight_documents_valid": documents.get("valid") is True,
        "errors": errors,
        "warnings": warnings,
        **boundary_payload(),
    }


def write_evidence_index(path: pathlib.Path, record: dict[str, Any], result: dict[str, Any], phase18: dict[str, Any], documents: dict[str, Any]) -> None:
    document_lines = "\n".join(f"- `{item['path']}`" for item in documents.get("documents", []))
    text = f"""# Phase 19 Controlled Beta Activation Preflight Evidence

- Controlled beta activation preflight recorded: {str(result.get('controlled_beta_activation_preflight_recorded') is True).lower()}
- Phase 18 launch governance valid: {str(result.get('phase_18_controlled_beta_launch_governance_valid') is True).lower()}
- Activation preflight documents valid: {str(result.get('activation_preflight_documents_valid') is True).lower()}
- Source commit: `{record.get('source_commit')}`
- Target branch: `{record.get('target_branch')}`

## Boundary

- Production release authorised: false
- Deployment authorised: false
- Release tag authorised: false
- Public beta authorised: false
- Controlled beta launch authorised: false
- Live learner traffic authorised: false
- Learner data migration authorised: false
- Runtime KG implementation claimed: false

## Checked Documents

{document_lines}

## Raw Evidence

- `raw/git_state.json`
- `raw/phase18_launch_governance_verification.json`
- `raw/activation_preflight_documents.json`
- `raw/activation_preflight_boundary.json`
- `raw/controlled_beta_activation_preflight_result.json`
- `raw/controlled_beta_activation_preflight_record_snapshot.json`
"""
    path.write_text(text, encoding="utf-8")


def write_sha256sums(evidence_dir: pathlib.Path) -> pathlib.Path:
    sums_path = evidence_dir / "SHA256SUMS.txt"
    lines: list[str] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{sha256_file(path)}  {path.as_posix()}\n")
    sums_path.write_text("".join(lines), encoding="utf-8")
    return sums_path


def capture(args: argparse.Namespace) -> dict[str, Any]:
    claimed = bool(args.claim_controlled_beta_activation_preflight)
    git = git_state(args.target_branch)
    phase18 = run_command(["python3", PHASE18_VERIFY.as_posix(), "--json"])
    docs = validate_preflight_documents()
    result = build_result(claimed=claimed, phase18=phase18, git=git, documents=docs)
    record = {
        "schema_version": 1,
        "slice": "PHASE-19-CONTROLLED-BETA-ACTIVATION-PREFLIGHT-AUTHORITY",
        "status": "controlled_beta_activation_preflight_recorded" if result["valid"] else "controlled_beta_activation_preflight_pending",
        "beta_scope": "controlled_beta_activation_preflight_gate",
        "controlled_beta_activation_preflight_claimed": claimed,
        "controlled_beta_activation_preflight_recorded": result["valid"],
        "preflight_owner": args.preflight_owner,
        "captured_at": utc_now(),
        "target_branch": args.target_branch,
        "source_commit": git.get("head_sha"),
        "remote_target_sha": git.get("remote_target_sha"),
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": (EVIDENCE_DIR / "evidence_index.md").as_posix(),
        "sha256sums": (EVIDENCE_DIR / "SHA256SUMS.txt").as_posix(),
        "phase_18_controlled_beta_launch_governance_valid": result["phase_18_controlled_beta_launch_governance_valid"],
        "activation_preflight_documents_valid": result["activation_preflight_documents_valid"],
        **boundary_payload(),
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    raw = EVIDENCE_DIR / "raw"
    write_json(raw / "git_state.json", git)
    write_json(raw / "phase18_launch_governance_verification.json", phase18)
    write_json(raw / "activation_preflight_documents.json", docs)
    write_json(raw / "activation_preflight_boundary.json", boundary_payload())
    write_json(raw / "controlled_beta_activation_preflight_result.json", result)
    write_json(raw / "controlled_beta_activation_preflight_record_snapshot.json", record)
    write_evidence_index(EVIDENCE_DIR / "evidence_index.md", record, result, phase18, docs)
    sums = write_sha256sums(EVIDENCE_DIR)
    record["sha256sums"] = sums.as_posix()
    write_json(RECORD_PATH, record)
    write_json(raw / "controlled_beta_activation_preflight_record_snapshot.json", record)
    write_sha256sums(EVIDENCE_DIR)

    output = {**result, "record": RECORD_PATH.as_posix(), "evidence_dir": EVIDENCE_DIR.as_posix()}
    if args.require_valid and not output["valid"]:
        raise SystemExit(json.dumps(output, indent=2, sort_keys=True))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-controlled-beta-activation-preflight", action="store_true")
    parser.add_argument("--preflight-owner", default="")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.claim_controlled_beta_activation_preflight and not args.preflight_owner.strip():
        raise SystemExit("--preflight-owner is required when claiming activation preflight")
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
