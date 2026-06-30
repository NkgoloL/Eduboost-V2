from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from urllib.parse import urlparse

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None
    RealDictCursor = None

ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/release/audit_write_runtime_evidence_status.json"
STATUS_MD = ROOT / "docs/release/audit_write_runtime_evidence_status.md"

ACCEPTED_STATUS = "audit-write-runtime-accepted"
NOT_ACCEPTED_STATUS = "audit-write-runtime-not-accepted"
AUDIT_TABLE = "audit_events"

PLACEHOLDER_TOKENS = {"<", ">", "TODO", "TBD", "REAL_", "example.com", "localhost", "127.0.0.1", "..."}


@dataclass(frozen=True)
class GitHubRunEvidence:
    run_id: str
    run_url: str
    workflow_name: str
    run_status: str
    conclusion: str
    head_sha: str
    blockers: list[str]


@dataclass(frozen=True)
class FlowCommandResult:
    command: str
    return_code: int | None
    output_excerpt: str


@dataclass(frozen=True)
class AuditWriteRuntimeEvidenceStatus:
    generated_at: str
    current_commit: str
    status: str
    db_url_label: str
    db_checked: bool
    audit_table_exists: bool
    audit_events_count_before: int | None
    audit_events_count_after: int | None
    audit_events_delta: int | None
    audit_trace_id: str
    audit_trace_detected: bool
    flow_result: FlowCommandResult
    github_run: GitHubRunEvidence
    verified_by: str
    date_verified: str
    blockers: list[str]


def _run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def current_commit() -> str:
    result = _run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token.lower() in lowered for token in PLACEHOLDER_TOKENS)


def normalize_db_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql://" + url.removeprefix("postgresql+asyncpg://")
    if url.startswith("postgres://"):
        return "postgresql://" + url.removeprefix("postgres://")
    return url


def _db_url() -> tuple[str, str]:
    for name in ["AUDIT_WRITE_DATABASE_URL", "DATABASE_URL", "STAGING_DATABASE_URL", "SUPABASE_DB_URL"]:
        value = _env(name)
        if value:
            return name, normalize_db_url(value)
    return "", ""


def valid_db_url(url: str) -> bool:
    if not url or has_placeholder(url):
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"postgresql", "postgres"} and bool(parsed.hostname)


def _gh_available() -> bool:
    return _run(["gh", "--version"]).returncode == 0


def _view_run(run_id: str) -> dict[str, Any] | None:
    result = _run(["gh", "run", "view", run_id, "--json", "databaseId,status,conclusion,headSha,url,workflowName,createdAt"])
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def collect_github_run_evidence(run_id: str, expected_sha: str) -> GitHubRunEvidence:
    blockers: list[str] = []
    if not run_id:
        blockers.append("AUDIT_WRITE_RUN_ID is required for accepted evidence")
        return GitHubRunEvidence("", "", "", "", "", "", blockers)
    if not re.fullmatch(r"[0-9]+", run_id):
        blockers.append("AUDIT_WRITE_RUN_ID is not numeric")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)
    if not _gh_available():
        blockers.append("GitHub CLI is unavailable or not authenticated")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)

    run = _view_run(run_id)
    if run is None:
        blockers.append(f"unable to read GitHub Actions run {run_id}")
        return GitHubRunEvidence(run_id, "", "", "", "", "", blockers)

    run_url = str(run.get("url") or f"https://github.com/NkgoloL/Eduboost-V2/actions/runs/{run_id}").strip()
    workflow_name = str(run.get("workflowName") or "").strip()
    run_status = str(run.get("status") or "").strip()
    conclusion = str(run.get("conclusion") or "").strip()
    head_sha = str(run.get("headSha") or "").strip()

    if f"/actions/runs/{run_id}" not in run_url:
        blockers.append("run URL does not contain numeric run ID")
    if run_status != "completed":
        blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")
    if conclusion != "success":
        blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")
    if head_sha != expected_sha:
        blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")
    if not workflow_name:
        blockers.append("workflow name is missing")

    return GitHubRunEvidence(run_id, run_url, workflow_name, run_status, conclusion, head_sha, blockers)


def _connect(db_url: str):
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed")
    return psycopg2.connect(db_url)


def _table_exists(conn, table_name: str) -> bool:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
              SELECT 1 FROM information_schema.tables
              WHERE table_schema = 'public' AND table_name = %s
            )
            """,
            (table_name,),
        )
        return bool(cursor.fetchone()[0])


def _count_rows(conn, table_name: str) -> int:
    with conn.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM public."{table_name}"')
        return int(cursor.fetchone()[0])


def _order_column(conn, table_name: str) -> str:
    preferred = ["created_at", "timestamp", "occurred_at", "updated_at", "id"]
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            """,
            (table_name,),
        )
        columns = {str(row[0]) for row in cursor.fetchall()}
    for column in preferred:
        if column in columns:
            return column
    return ""


def _latest_rows(conn, table_name: str, *, limit: int = 50) -> list[dict[str, Any]]:
    if RealDictCursor is None:
        return []
    order_column = _order_column(conn, table_name)
    order_sql = f'ORDER BY "{order_column}" DESC' if order_column else ""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f'SELECT * FROM public."{table_name}" {order_sql} LIMIT %s', (limit,))
        return [dict(row) for row in cursor.fetchall()]


def _trace_detected(rows: list[dict[str, Any]], trace_id: str) -> bool:
    if not trace_id:
        return False
    for row in rows:
        rendered = json.dumps(row, default=str, sort_keys=True)
        if trace_id in rendered:
            return True
    return False


def _run_flow_command(command: str, trace_id: str) -> FlowCommandResult:
    if not command:
        return FlowCommandResult("", None, "")
    env = {**os.environ, "AUDIT_WRITE_TRACE_ID": trace_id}
    result = subprocess.run(["bash", "-c", command], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return FlowCommandResult(command=command, return_code=result.returncode, output_excerpt=result.stdout[-5000:])


def write_status(*, run_flow: bool = False) -> AuditWriteRuntimeEvidenceStatus:
    blockers: list[str] = []
    sha = current_commit()
    accept = _env("AUDIT_WRITE_ACCEPT") == "1"

    db_label, db_url = _db_url()
    trace_id = _env("AUDIT_WRITE_TRACE_ID") or f"audit-write-{sha[:12]}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    flow_command = _env("AUDIT_WRITE_FLOW_COMMAND")

    db_checked = False
    audit_table_exists = False
    before_count: int | None = None
    after_count: int | None = None
    delta: int | None = None
    trace_found = False
    flow_result = FlowCommandResult(flow_command, None, "")

    if not valid_db_url(db_url):
        blockers.append("AUDIT_WRITE_DATABASE_URL/DATABASE_URL is missing, placeholder, local, or invalid")
    else:
        try:
            with _connect(db_url) as conn:
                db_checked = True
                audit_table_exists = _table_exists(conn, AUDIT_TABLE)
                if not audit_table_exists:
                    blockers.append("audit_events table is missing")
                else:
                    before_count = _count_rows(conn, AUDIT_TABLE)
                    if run_flow:
                        flow_result = _run_flow_command(flow_command, trace_id)
                        if flow_result.return_code != 0:
                            blockers.append(f"flow command failed with exit code {flow_result.return_code}")
                    after_count = _count_rows(conn, AUDIT_TABLE)
                    delta = after_count - before_count if before_count is not None else None
                    trace_found = _trace_detected(_latest_rows(conn, AUDIT_TABLE), trace_id)
                    if run_flow:
                        if (delta is None or delta <= 0) and not trace_found:
                            blockers.append("audit_events did not increase and trace ID was not found")
                        if after_count <= 0:
                            blockers.append("audit_events has no rows after audited flow")
        except Exception as exc:
            blockers.append(f"database audit-write check failed: {type(exc).__name__}: {exc}")

    if accept:
        if not run_flow and _env("AUDIT_WRITE_ATTACH_ONLY") != "1":
            blockers.append("accepted evidence requires run_flow unless AUDIT_WRITE_ATTACH_ONLY=1")
        if not flow_command or has_placeholder(flow_command):
            blockers.append("AUDIT_WRITE_FLOW_COMMAND is missing or placeholder")
        if _env("AUDIT_WRITE_FLOW_RESULT") and _env("AUDIT_WRITE_FLOW_RESULT") != "passed":
            blockers.append("AUDIT_WRITE_FLOW_RESULT must be passed when provided")
        github = collect_github_run_evidence(_env("AUDIT_WRITE_RUN_ID"), sha)
        blockers.extend(github.blockers)
    else:
        github = GitHubRunEvidence("", "", "", "", "", "", [])

    status = ACCEPTED_STATUS if accept and not blockers else NOT_ACCEPTED_STATUS
    result = AuditWriteRuntimeEvidenceStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=sha,
        status=status,
        db_url_label=db_label,
        db_checked=db_checked,
        audit_table_exists=audit_table_exists,
        audit_events_count_before=before_count,
        audit_events_count_after=after_count,
        audit_events_delta=delta,
        audit_trace_id=trace_id,
        audit_trace_detected=trace_found,
        flow_result=flow_result,
        github_run=github,
        verified_by="github-actions" if status == ACCEPTED_STATUS else "unverified",
        date_verified=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        blockers=blockers,
    )
    STATUS_JSON.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    _write_markdown(result)
    return result


def _write_markdown(status: AuditWriteRuntimeEvidenceStatus) -> None:
    lines = [
        "# Audit Write Runtime Evidence Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**DB URL label:** `{status.db_url_label}`",
        f"**DB checked:** `{status.db_checked}`",
        f"**audit_events exists:** `{status.audit_table_exists}`",
        f"**audit_events before:** `{status.audit_events_count_before}`",
        f"**audit_events after:** `{status.audit_events_count_after}`",
        f"**audit_events delta:** `{status.audit_events_delta}`",
        f"**Trace ID:** `{status.audit_trace_id}`",
        f"**Trace detected:** `{status.audit_trace_detected}`",
        f"**Flow command:** `{status.flow_result.command}`",
        f"**Flow return code:** `{status.flow_result.return_code}`",
        f"**Run ID:** `{status.github_run.run_id}`",
        f"**Run URL:** `{status.github_run.run_url}`",
        f"**Workflow:** `{status.github_run.workflow_name}`",
        "",
        "## Flow output excerpt",
        "",
        "```text",
        status.flow_result.output_excerpt,
        "```",
        "",
        "## Blockers",
        "",
    ]
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## No false-closure rules",
        "",
        "- This proof closes AUDIT-WRITE-001 only in AUDIT_WRITE_ACCEPT=1 mode.",
        "- A real flow command must run successfully.",
        "- The audit_events table must contain rows after the flow.",
        "- Either audit_events count must increase or the trace ID must be found in recent audit rows.",
        "- A successful GitHub Actions run matching current commit is required.",
        "- This proof does not close JWT, ARQ, DIAG-SCORE, approvals, frontend runtime, backup/restore/rollback, or beta release.",
        "",
    ])
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-flow", action="store_true")
    args = parser.parse_args()
    result = write_status(run_flow=args.run_flow)
    print(result.status)
    print(f"audit_events_before={result.audit_events_count_before}")
    print(f"audit_events_after={result.audit_events_count_after}")
    print(f"audit_events_delta={result.audit_events_delta}")
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
        raise SystemExit(1)
