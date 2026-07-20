#!/usr/bin/env python3
"""Capture real hosted GitHub Actions evidence for TA Phase 09.

This script is intentionally conservative: it records a hosted CI run only when
GitHub reports a completed, successful Actions run for the requested branch and
commit SHA. Otherwise it writes a formal unclaimed record rather than inventing
success.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
from scripts._subprocess import run
import sys
from typing import Any

RECORD_PATH = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json"
)
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/technical-audit/phase-09-hosted-ci")
RAW_DIR = EVIDENCE_DIR / "raw"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(cmd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_value(args: list[str], default: str | None = None) -> str | None:
    try:
        return run(["git", *args]).stdout.strip()
    except Exception:
        return default


def require_gh() -> None:
    try:
        run(["gh", "--version"])
    except Exception as exc:
        raise SystemExit(
            "GitHub CLI 'gh' is required to capture hosted CI evidence. "
            "Install gh, authenticate with `gh auth login`, then rerun this script."
        ) from exc


def load_json_stdout(cmd: list[str]) -> Any:
    completed = run(cmd)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Command returned invalid JSON: {' '.join(cmd)}\n{completed.stdout}") from exc


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256sums(files: list[pathlib.Path], sums_path: pathlib.Path) -> dict[str, str]:
    sums: dict[str, str] = {}
    lines: list[str] = []
    for file_path in files:
        digest = sha256_file(file_path)
        rel = file_path.as_posix()
        sums[rel] = digest
        lines.append(f"{digest}  {rel}")
    sums_path.parent.mkdir(parents=True, exist_ok=True)
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sums


def gh_repo_from_origin() -> str | None:
    url = git_value(["remote", "get-url", "origin"])
    if not url:
        return None
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def select_run(runs: list[dict[str, Any]], sha: str, workflow_name: str | None) -> dict[str, Any] | None:
    candidates = [r for r in runs if r.get("headSha") == sha]
    if workflow_name:
        candidates = [r for r in candidates if r.get("workflowName") == workflow_name]
    successful = [
        r for r in candidates if r.get("status") == "completed" and r.get("conclusion") == "success"
    ]
    if successful:
        return successful[0]
    return candidates[0] if candidates else None


def fetch_branch_protection(repo: str, target_branch: str, raw_dir: pathlib.Path) -> tuple[bool, pathlib.Path | None, dict[str, Any] | None]:
    raw_path = raw_dir / f"branch_protection_{target_branch}.json"
    cmd = ["gh", "api", f"repos/{repo}/branches/{target_branch}/protection"]
    completed = run(cmd, check=False)
    payload: dict[str, Any]
    if completed.returncode == 0:
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = {
                "available": False,
                "reason": "invalid_json_from_gh_api",
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
    else:
        payload = {
            "available": False,
            "reason": "gh_api_failed_or_branch_unprotected",
            "returncode": completed.returncode,
            "stderr": completed.stderr.strip(),
        }
    write_json(raw_path, payload)
    claimed = bool(payload) and payload.get("available") is not False and "url" in payload
    return claimed, raw_path, payload


def build_unclaimed_record(
    *,
    repo: str | None,
    branch: str,
    sha: str,
    workflow_name: str | None,
    reason: str,
    raw_files: list[pathlib.Path],
    branch_protection_claimed: bool,
    branch_protection_file: pathlib.Path | None,
    sums_path: pathlib.Path,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "slice": "TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE",
        "status": "hosted_ci_unclaimed",
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "repository": repo,
        "branch": branch,
        "head_sha": sha,
        "workflow_name": workflow_name,
        "hosted_ci_run_claimed": False,
        "hosted_ci_unclaimed_reason": reason,
        "hosted_ci_conclusion": None,
        "hosted_ci_status": None,
        "hosted_ci_run_id": None,
        "hosted_ci_run_url": None,
        "branch_protection_claimed": branch_protection_claimed,
        "branch_protection_evidence": branch_protection_file.as_posix() if branch_protection_file else None,
        "merge_readiness_authorised": False,
        "raw_evidence_files": [p.as_posix() for p in raw_files],
        "sha256sums": sums_path.as_posix(),
        "constraints": [
            "Hosted CI success is not claimed unless GitHub Actions reports a completed successful run.",
            "Merge readiness is not authorised unless hosted CI evidence and branch-protection evidence are both recorded.",
            "This record may pass local verification only with --allow-unclaimed while awaiting hosted CI evidence.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GH_REPO") or gh_repo_from_origin())
    parser.add_argument("--branch", default=git_value(["branch", "--show-current"], "HEAD"))
    parser.add_argument("--sha", default=git_value(["rev-parse", "HEAD"]))
    parser.add_argument("--workflow", default=os.environ.get("GITHUB_WORKFLOW") or "EduBoost Hosted CI Authority")
    parser.add_argument("--target-branch", default=os.environ.get("TARGET_BRANCH", "master"))
    parser.add_argument("--record-path", default=str(RECORD_PATH))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--require-success", action="store_true", help="Exit non-zero unless a successful hosted CI run is captured.")
    parser.add_argument("--require-branch-protection", action="store_true", help="Exit non-zero unless branch protection evidence is captured.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.sha or not SHA_RE.match(args.sha):
        raise SystemExit(f"Invalid or missing commit SHA: {args.sha!r}")
    if not args.repo:
        raise SystemExit("Could not infer GitHub repo. Pass --repo OWNER/REPO or set GH_REPO.")

    require_gh()

    record_path = pathlib.Path(args.record_path)
    evidence_dir = pathlib.Path(args.evidence_dir)
    raw_dir = evidence_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    run_list = load_json_stdout(
        [
            "gh",
            "run",
            "list",
            "--repo",
            args.repo,
            "--branch",
            args.branch,
            "--limit",
            str(args.limit),
            "--json",
            "databaseId,displayTitle,headBranch,headSha,conclusion,status,url,workflowName,event,createdAt,updatedAt",
        ]
    )
    run_list_path = raw_dir / "gh_run_list.json"
    write_json(run_list_path, run_list)

    branch_protection_claimed, branch_protection_file, _ = fetch_branch_protection(
        args.repo, args.target_branch, raw_dir
    )

    selected = select_run(run_list, args.sha, args.workflow)
    raw_files = [run_list_path]
    if branch_protection_file:
        raw_files.append(branch_protection_file)

    if not selected:
        sums_path = evidence_dir / "SHA256SUMS.txt"
        write_sha256sums(raw_files, sums_path)
        record = build_unclaimed_record(
            repo=args.repo,
            branch=args.branch,
            sha=args.sha,
            workflow_name=args.workflow,
            reason="no_github_actions_run_found_for_requested_branch_sha_and_workflow",
            raw_files=raw_files,
            branch_protection_claimed=branch_protection_claimed,
            branch_protection_file=branch_protection_file,
            sums_path=sums_path,
        )
        write_json(record_path, record)
        print(json.dumps({"valid": False, "reason": record["hosted_ci_unclaimed_reason"], "record": str(record_path)}, indent=2))
        return 2 if args.require_success else 0

    run_id = selected.get("databaseId")
    view = load_json_stdout(
        [
            "gh",
            "run",
            "view",
            str(run_id),
            "--repo",
            args.repo,
            "--json",
            "databaseId,displayTitle,headBranch,headSha,conclusion,status,url,workflowName,event,createdAt,updatedAt,jobs",
        ]
    )
    run_view_path = raw_dir / f"gh_run_view_{run_id}.json"
    write_json(run_view_path, view)
    raw_files.append(run_view_path)

    hosted_ok = view.get("status") == "completed" and view.get("conclusion") == "success" and view.get("headSha") == args.sha
    if not hosted_ok:
        sums_path = evidence_dir / "SHA256SUMS.txt"
        write_sha256sums(raw_files, sums_path)
        record = build_unclaimed_record(
            repo=args.repo,
            branch=args.branch,
            sha=args.sha,
            workflow_name=args.workflow,
            reason="github_actions_run_found_but_not_completed_success_for_requested_sha",
            raw_files=raw_files,
            branch_protection_claimed=branch_protection_claimed,
            branch_protection_file=branch_protection_file,
            sums_path=sums_path,
        )
        record["hosted_ci_run_id"] = run_id
        record["hosted_ci_run_url"] = view.get("url") or selected.get("url")
        record["hosted_ci_status"] = view.get("status")
        record["hosted_ci_conclusion"] = view.get("conclusion")
        write_json(record_path, record)
        print(json.dumps({"valid": False, "reason": record["hosted_ci_unclaimed_reason"], "record": str(record_path)}, indent=2))
        return 2 if args.require_success else 0

    sums_path = evidence_dir / "SHA256SUMS.txt"
    write_sha256sums(raw_files, sums_path)

    merge_ready = bool(hosted_ok and branch_protection_claimed)
    record = {
        "schema_version": 1,
        "slice": "TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE",
        "status": "hosted_ci_evidence_recorded" if hosted_ok else "hosted_ci_unclaimed",
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "repository": args.repo,
        "branch": args.branch,
        "target_branch": args.target_branch,
        "head_sha": args.sha,
        "workflow_name": view.get("workflowName") or args.workflow,
        "hosted_ci_run_claimed": True,
        "hosted_ci_status": view.get("status"),
        "hosted_ci_conclusion": view.get("conclusion"),
        "hosted_ci_run_id": run_id,
        "hosted_ci_run_url": view.get("url") or selected.get("url"),
        "hosted_ci_event": view.get("event") or selected.get("event"),
        "hosted_ci_created_at": view.get("createdAt") or selected.get("createdAt"),
        "hosted_ci_updated_at": view.get("updatedAt") or selected.get("updatedAt"),
        "branch_protection_claimed": branch_protection_claimed,
        "branch_protection_evidence": branch_protection_file.as_posix() if branch_protection_file else None,
        "merge_readiness_authorised": merge_ready,
        "raw_evidence_files": [p.as_posix() for p in raw_files],
        "sha256sums": sums_path.as_posix(),
        "constraints": [
            "Hosted CI success is backed by a real GitHub Actions run view payload.",
            "Merge readiness is authorised only when branch protection evidence is also present.",
            "Evidence files are protected by SHA-256 sums generated at capture time.",
        ],
    }
    write_json(record_path, record)

    result = {
        "valid": True,
        "record": str(record_path),
        "run_id": run_id,
        "run_url": record["hosted_ci_run_url"],
        "merge_readiness_authorised": merge_ready,
        "branch_protection_claimed": branch_protection_claimed,
    }
    print(json.dumps(result, indent=2))

    if args.require_branch_protection and not branch_protection_claimed:
        print("Branch protection evidence was not captured; merge readiness remains unauthorised.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
