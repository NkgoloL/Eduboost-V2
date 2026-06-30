from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs/release/staging_smoke_evidence_status.json"
OUT_MD = ROOT / "docs/release/staging_smoke_evidence_status.md"
LEGACY_MD = ROOT / "docs/release/staging_smoke_evidence.md"

ACCEPTED_STATUS = "staging-smoke-evidence-accepted"
NOT_ACCEPTED_STATUS = "staging-smoke-evidence-not-accepted"

PLACEHOLDER_TOKENS = {
    "example.com",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "<",
    ">",
    "REAL_",
    "TODO",
    "TBD",
    "...",
}


@dataclass(frozen=True)
class StagingSmokeEvidenceStatus:
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
    staging_base_url: str
    smoke_command: str
    smoke_result: str
    healthcheck_result: str
    api_result: str
    frontend_result: str
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


def _candidate_staging_run_for_commit(branch: str, sha: str) -> dict[str, Any] | None:
    result = _run(
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
        ]
    )
    if result.returncode != 0:
        return None

    data = _parse_json(result.stdout, [])
    if not isinstance(data, list):
        return None

    for run in data:
        if not isinstance(run, dict):
            continue
        workflow = str(run.get("workflowName", "")).lower()
        if str(run.get("headSha", "")).strip() != sha:
            continue
        if str(run.get("status", "")).strip() != "completed":
            continue
        if str(run.get("conclusion", "")).strip() != "success":
            continue
        if "staging" not in workflow and "smoke" not in workflow:
            continue
        return run

    return None


def _run_id_from_data(data: dict[str, Any]) -> str:
    return str(data.get("databaseId") or "").strip()


def _run_url_from_data(data: dict[str, Any], run_id: str) -> str:
    url = str(data.get("url") or "").strip()
    if url:
        return url
    return f"https://github.com/NkgoloL/Eduboost-V2/actions/runs/{run_id}"


def _has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token.lower() in lowered for token in PLACEHOLDER_TOKENS)


def _valid_staging_url(value: str) -> bool:
    if not value:
        return False
    if _has_placeholder(value):
        return False
    parsed = urlparse(value)
    if parsed.scheme != "https":
        return False
    if not parsed.netloc:
        return False
    return True


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def collect_staging_smoke_evidence() -> StagingSmokeEvidenceStatus:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha = current_commit()
    branch = current_branch()
    blockers: list[str] = []

    requested_run_id = _env("STAGING_SMOKE_RUN_ID") or _env("STAGING_EVIDENCE_RUN_ID")
    expected_workflow = _env("STAGING_SMOKE_WORKFLOW_NAME")

    if not _gh_available():
        blockers.append("GitHub CLI is unavailable or not authenticated")

    run: dict[str, Any] | None = None
    if requested_run_id:
        if not re.fullmatch(r"[0-9]+", requested_run_id):
            blockers.append("STAGING_SMOKE_RUN_ID is not numeric")
        elif _gh_available():
            run = _view_run(requested_run_id)
            if run is None:
                blockers.append(f"unable to read GitHub Actions run {requested_run_id}")
    elif _gh_available():
        run = _candidate_staging_run_for_commit(branch, sha)
        if run is None:
            blockers.append(
                "no successful staging/smoke GitHub Actions run found for current commit; set STAGING_SMOKE_RUN_ID"
            )

    if run is None:
        run = {}

    run_id = _run_id_from_data(run) or requested_run_id
    run_url = _run_url_from_data(run, run_id) if run_id else ""
    workflow_name = str(run.get("workflowName") or "").strip()
    run_status = str(run.get("status") or "").strip()
    conclusion = str(run.get("conclusion") or "").strip()
    head_sha = str(run.get("headSha") or "").strip()

    staging_base_url = _env("STAGING_SMOKE_BASE_URL") or _env("STAGING_BASE_URL")
    smoke_command = _env("STAGING_SMOKE_TEST_COMMAND") or _env("STAGING_SMOKE_COMMAND")
    smoke_result = _env("STAGING_SMOKE_RESULT")
    healthcheck_result = _env("STAGING_SMOKE_HEALTHCHECK_RESULT")
    api_result = _env("STAGING_SMOKE_API_RESULT")
    frontend_result = _env("STAGING_SMOKE_FRONTEND_RESULT") or "not-recorded"

    if not re.fullmatch(r"[0-9]+", run_id or ""):
        blockers.append("run ID is missing or non-numeric")

    if run_id and f"/actions/runs/{run_id}" not in run_url:
        blockers.append("run URL does not contain the numeric run ID")

    if _has_placeholder(run_url):
        blockers.append("run URL contains placeholder evidence")

    if run_status != "completed":
        blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")

    if conclusion != "success":
        blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")

    if head_sha != sha:
        blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {sha}")

    if not workflow_name:
        blockers.append("workflow name is missing")

    if expected_workflow and workflow_name != expected_workflow:
        blockers.append(
            f"workflow name {workflow_name!r} does not match expected {expected_workflow!r}"
        )

    if workflow_name and "auth refresh db proof" in workflow_name.lower():
        blockers.append("auth refresh DB proof workflow is not valid staging smoke evidence")

    if not _valid_staging_url(staging_base_url):
        blockers.append("staging base URL is missing, non-HTTPS, localhost/example, or placeholder")

    if not smoke_command or _has_placeholder(smoke_command):
        blockers.append("staging smoke test command is missing or placeholder")

    if smoke_result != "passed":
        blockers.append("STAGING_SMOKE_RESULT must be passed")

    if healthcheck_result != "passed":
        blockers.append("STAGING_SMOKE_HEALTHCHECK_RESULT must be passed")

    if api_result != "passed":
        blockers.append("STAGING_SMOKE_API_RESULT must be passed")

    if frontend_result not in {"passed", "not-recorded"}:
        blockers.append("STAGING_SMOKE_FRONTEND_RESULT must be passed or omitted")

    status = ACCEPTED_STATUS if not blockers else NOT_ACCEPTED_STATUS

    return StagingSmokeEvidenceStatus(
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
        staging_base_url=staging_base_url,
        smoke_command=smoke_command,
        smoke_result=smoke_result,
        healthcheck_result=healthcheck_result,
        api_result=api_result,
        frontend_result=frontend_result,
        verified_by="github-actions" if status == ACCEPTED_STATUS else "unverified",
        date_verified=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        blockers=blockers,
    )


def write_status() -> StagingSmokeEvidenceStatus:
    status = collect_staging_smoke_evidence()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")

    lines = [
        "# Staging Smoke Evidence Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        f"Branch: `{status.current_branch}`",
        "",
        f"**Status:** `{status.status}`",
        "<!-- Status: pending runtime execution -->",
        f"**Run ID:** `{status.run_id}`",
        f"**Run URL:** `{status.run_url}`",
        f"**Workflow:** `{status.workflow_name}`",
        f"**Run status:** `{status.run_status}`",
        f"**Conclusion:** `{status.conclusion}`",
        f"**Head SHA:** `{status.head_sha}`",
        f"**Staging base URL:** `{status.staging_base_url}`",
        f"**Smoke command:** `{status.smoke_command}`",
        f"**Smoke result:** `{status.smoke_result}`",
        f"**Healthcheck result:** `{status.healthcheck_result}`",
        f"**API result:** `{status.api_result}`",
        f"**Frontend result:** `{status.frontend_result}`",
        f"**Verified by:** `{status.verified_by}`",
        f"**Date verified:** `{status.date_verified}`",
        "",
        "## Required Runtime Smoke Coverage",
        "",
        "Status: pending runtime execution",
        "",
        "TODO before acceptance:",
        "",
        "- GET /api/v2/health/deep",
        "- Auth register/login/refresh/logout",
        "- POPIA data export route",
        "- Frontend critical learner flow",
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
            "- The staging URL must be a real non-placeholder HTTPS URL.",
            "- The smoke command and result metadata must be explicit.",
            "- The auth refresh DB proof workflow is not staging smoke evidence.",
            "- This staging smoke evidence does not close legal/security/content approvals, JWT rotation, ARQ live Redis evidence, diagnostics live DB proof, lesson auth staging proof, or diagnostic scoring audit.",
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
