from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/ci_evidence_status.json"
OUT_MD = ROOT / "docs/release/ci_evidence_status.md"
LEGACY_MD = ROOT / "docs/release/ci_evidence.md"

ACCEPTED_STATUS = "ci-evidence-accepted"
NOT_ACCEPTED_STATUS = "ci-evidence-not-accepted"

REJECTED_WORKFLOW_NAME_FRAGMENTS = {
    "auth refresh db proof",
    "refresh db proof",
}


@dataclass(frozen=True)
class CiEvidenceStatus:
    generated_at: str
    current_commit: str
    current_branch: str
    status: str
    run_id: str
    run_url: str
    workflow_name: str
    run_status: str
    conclusion: str
    head_sha: str
    verified_by: str
    date_verified: str
    blockers: list[str]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def current_commit() -> str:
    result = _run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def current_branch() -> str:
    result = _run(["git", "branch", "--show-current"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _parse_json(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return fallback


def _gh_available() -> bool:
    result = _run(["gh", "--version"])
    return result.returncode == 0


def _view_run(run_id: str) -> dict[str, Any] | None:
    result = _run(
        [
            "gh",
            "run",
            "view",
            run_id,
            "--json",
            "databaseId,status,conclusion,headSha,url,workflowName,createdAt",
        ]
    )
    if result.returncode != 0:
        return None
    data = _parse_json(result.stdout, None)
    return data if isinstance(data, dict) else None


def _latest_successful_run_for_commit(branch: str, sha: str) -> dict[str, Any] | None:
    commands = [
        [
            "gh",
            "run",
            "list",
            "--branch",
            branch,
            "--commit",
            sha,
            "--limit",
            "30",
            "--json",
            "databaseId,status,conclusion,headSha,url,workflowName,createdAt",
        ],
        [
            "gh",
            "run",
            "list",
            "--branch",
            branch,
            "--limit",
            "50",
            "--json",
            "databaseId,status,conclusion,headSha,url,workflowName,createdAt",
        ],
    ]

    for command in commands:
        result = _run(command)
        if result.returncode != 0:
            continue
        data = _parse_json(result.stdout, [])
        if not isinstance(data, list):
            continue

        for run in data:
            if not isinstance(run, dict):
                continue
            if str(run.get("headSha", "")).strip() != sha:
                continue
            if str(run.get("status", "")).strip() != "completed":
                continue
            if str(run.get("conclusion", "")).strip() != "success":
                continue
            if _workflow_is_rejected(str(run.get("workflowName", ""))):
                continue
            return run

    return None


def _workflow_is_rejected(workflow_name: str) -> bool:
    lowered = workflow_name.strip().lower()
    return any(fragment in lowered for fragment in REJECTED_WORKFLOW_NAME_FRAGMENTS)


def _run_id_from_data(data: dict[str, Any]) -> str:
    return str(data.get("databaseId") or data.get("run_id") or "").strip()


def _run_url_from_data(data: dict[str, Any], run_id: str) -> str:
    url = str(data.get("url") or "").strip()
    if url:
        return url
    return f"https://github.com/NkgoloL/Eduboost-V2/actions/runs/{run_id}"


def collect_ci_evidence() -> CiEvidenceStatus:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha = current_commit()
    branch = current_branch()
    blockers: list[str] = []

    if not _gh_available():
        blockers.append("GitHub CLI is unavailable or not authenticated")

    requested_run_id = os.getenv("CI_EVIDENCE_RUN_ID", "").strip()
    expected_workflow = os.getenv("CI_EVIDENCE_WORKFLOW_NAME", "").strip()

    run: dict[str, Any] | None = None

    if requested_run_id:
        if not re.fullmatch(r"[0-9]+", requested_run_id):
            blockers.append("CI_EVIDENCE_RUN_ID is not numeric")
        elif _gh_available():
            run = _view_run(requested_run_id)
            if run is None:
                blockers.append(f"unable to read GitHub Actions run {requested_run_id}")
    elif _gh_available():
        run = _latest_successful_run_for_commit(branch, sha)
        if run is None:
            blockers.append("no successful non-auth-refresh GitHub Actions run found for current commit")

    if run is None:
        run = {}

    run_id = _run_id_from_data(run) or requested_run_id
    workflow_name = str(run.get("workflowName") or "").strip()
    run_status = str(run.get("status") or "").strip()
    conclusion = str(run.get("conclusion") or "").strip()
    head_sha = str(run.get("headSha") or "").strip()
    run_url = _run_url_from_data(run, run_id) if run_id else ""

    if not re.fullmatch(r"[0-9]+", run_id or ""):
        blockers.append("run ID is missing or non-numeric")

    if run_id and f"/actions/runs/{run_id}" not in run_url:
        blockers.append("run URL does not contain the numeric run ID")

    if "example.com" in run_url or "REAL_RUN_ID" in run_url or "<" in run_url or ">" in run_url:
        blockers.append("run URL contains placeholder evidence")

    if run_status != "completed":
        blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")

    if conclusion != "success":
        blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")

    if head_sha != sha:
        blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {sha}")

    if not workflow_name:
        blockers.append("workflow name is missing")

    if workflow_name and _workflow_is_rejected(workflow_name):
        blockers.append(f"workflow {workflow_name!r} is not valid general CI evidence")

    if expected_workflow and workflow_name != expected_workflow:
        blockers.append(
            f"workflow name {workflow_name!r} does not match expected {expected_workflow!r}"
        )

    status = ACCEPTED_STATUS if not blockers else NOT_ACCEPTED_STATUS

    return CiEvidenceStatus(
        generated_at=generated_at,
        current_commit=sha,
        current_branch=branch,
        status=status,
        run_id=run_id,
        run_url=run_url,
        workflow_name=workflow_name,
        run_status=run_status,
        conclusion=conclusion,
        head_sha=head_sha,
        verified_by="github-actions" if status == ACCEPTED_STATUS else "unverified",
        date_verified=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        blockers=blockers,
    )


def write_status() -> CiEvidenceStatus:
    status = collect_ci_evidence()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# CI Evidence Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        f"Branch: `{status.current_branch}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Run ID:** `{status.run_id}`",
        f"**Run URL:** `{status.run_url}`",
        f"**Workflow:** `{status.workflow_name}`",
        f"**Run status:** `{status.run_status}`",
        f"**Conclusion:** `{status.conclusion}`",
        f"**Head SHA:** `{status.head_sha}`",
        f"**Verified by:** `{status.verified_by}`",
        f"**Date verified:** `{status.date_verified}`",
        "",
        "## Blockers",
        "",
    ]

    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- The accepted run must be completed and successful.",
            "- The accepted run must match the current commit SHA.",
            "- Placeholder run URLs or placeholder SHAs are rejected.",
            "- The auth refresh DB proof workflow is not accepted as general CI evidence.",
            "- This CI evidence does not close staging, external approvals, JWT rotation, ARQ live Redis evidence, diagnostics live DB proof, lesson authorization staging proof, or diagnostic scoring audit.",
            "",
        ]
    )

    rendered = "\n".join(lines)
    OUT_MD.write_text(rendered, encoding="utf-8")
    LEGACY_MD.write_text(rendered, encoding="utf-8")
    return status


if __name__ == "__main__":
    result = write_status()
    print(result.status)
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
        raise SystemExit(1)
