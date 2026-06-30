from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlparse

try:
    import psycopg2
except Exception:
    psycopg2 = None

ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/release/db_backup_restore_rollback_evidence_status.json"
STATUS_MD = ROOT / "docs/release/db_backup_restore_rollback_evidence_status.md"
WORK_DIR = ROOT / "temp/db_rollback"

ACCEPTED = "db-backup-restore-rollback-accepted"
NOT_ACCEPTED = "db-backup-restore-rollback-not-accepted"

KEY_TABLES = [
    "alembic_version",
    "audit_events",
    "diagnostic_items",
    "irt_items",
    "parental_consents",
]

PLACEHOLDER_TOKENS = ["<", ">", "TODO", "TBD", "example.com", "localhost", "127.0.0.1", "..."]


def env(name: str) -> str:
    return os.getenv(name, "").strip()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def current_commit() -> str:
    result = run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(token.lower() in lowered for token in PLACEHOLDER_TOKENS)


def normalize_db_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql://" + url.removeprefix("postgresql+asyncpg://")
    if url.startswith("postgres://"):
        return "postgresql://" + url.removeprefix("postgres://")
    return url


def valid_db_url(url: str, *, allow_localhost: bool = False) -> bool:
    if not url:
        return False
    # Allow localhost/127.0.0.1 for the restore target (service containers in CI)
    if allow_localhost:
        # Only block obvious template placeholders, not localhost
        blocked = [t for t in PLACEHOLDER_TOKENS if t not in ("localhost", "127.0.0.1")]
        lowered = url.lower()
        if any(token.lower() in lowered for token in blocked):
            return False
    elif has_placeholder(url):
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"postgresql", "postgres"} and bool(parsed.hostname) and bool(parsed.path.strip("/"))


def db_label(url: str, label: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    host = parsed.hostname or "unknown-host"
    port = parsed.port or ("6543" if "pooler" in host else "5432")
    db = parsed.path.strip("/") or "unknown-db"
    return f"{label}:{host}:{port}/{db}"


def source_url() -> tuple[str, str]:
    for name in ["DB_ROLLBACK_SOURCE_DATABASE_URL", "BACKUP_SOURCE_DATABASE_URL", "STAGING_DATABASE_URL", "DATABASE_URL"]:
        value = env(name)
        if value:
            return name, normalize_db_url(value)
    return "", ""


def restore_url() -> tuple[str, str]:
    for name in ["DB_ROLLBACK_RESTORE_DATABASE_URL", "RESTORE_DATABASE_URL", "DISPOSABLE_DATABASE_URL"]:
        value = env(name)
        if value:
            return name, normalize_db_url(value)
    return "", ""


def connect(url: str):
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed")
    return psycopg2.connect(url)


def table_exists(conn, table: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
              SELECT 1 FROM information_schema.tables
              WHERE table_schema='public' AND table_name=%s
            )
            """,
            (table,),
        )
        return bool(cur.fetchone()[0])


def table_count(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
            """
        )
        return int(cur.fetchone()[0])


def count_table(conn, table: str) -> int | None:
    if not table_exists(conn, table):
        return None
    with conn.cursor() as cur:
        cur.execute(f'SELECT COUNT(*) FROM public."{table}"')
        return int(cur.fetchone()[0])


def alembic_version(conn) -> str:
    if not table_exists(conn, "alembic_version"):
        return ""
    with conn.cursor() as cur:
        cur.execute('SELECT version_num FROM public."alembic_version" ORDER BY version_num')
        return ",".join(str(row[0]) for row in cur.fetchall())


def smoke(url: str) -> dict:
    out = {
        "connected": False,
        "table_count": None,
        "alembic_version": "",
        "key_table_counts": {},
        "blockers": [],
    }
    try:
        with connect(url) as conn:
            out["connected"] = True
            out["table_count"] = table_count(conn)
            out["alembic_version"] = alembic_version(conn)
            out["key_table_counts"] = {table: count_table(conn, table) for table in KEY_TABLES}
    except Exception as exc:
        out["blockers"].append(f"database smoke failed: {type(exc).__name__}: {exc}")

    if out["connected"] and not out["alembic_version"]:
        out["blockers"].append("alembic_version not detected")
    if out["connected"] and (out["table_count"] is None or out["table_count"] <= 0):
        out["blockers"].append("no public tables detected")
    return out


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_evidence(label: str, result: subprocess.CompletedProcess[str]) -> dict:
    excerpt = (result.stdout or "")[-5000:]
    if excerpt.strip():
        print(f"[{label}] output:\n{excerpt}", flush=True)
    return {
        "command_label": label,
        "return_code": result.returncode,
        "output_excerpt": excerpt,
    }


def empty_command(label: str = "") -> dict:
    return {"command_label": label, "return_code": None, "output_excerpt": ""}


def gh_run(run_id: str, expected_sha: str) -> dict:
    blockers: list[str] = []
    evidence = {
        "run_id": run_id,
        "run_url": "",
        "workflow_name": "",
        "run_status": "",
        "conclusion": "",
        "head_sha": "",
        "blockers": blockers,
    }
    if not run_id:
        blockers.append("DB_ROLLBACK_RUN_ID is required")
        return evidence
    if not re.fullmatch(r"[0-9]+", run_id):
        blockers.append("DB_ROLLBACK_RUN_ID is not numeric")
        return evidence
    if run(["gh", "--version"]).returncode != 0:
        blockers.append("GitHub CLI is unavailable")
        return evidence

    result = run([
        "gh", "run", "view", run_id,
        "--json", "status,conclusion,headSha,url,workflowName",
    ])
    if result.returncode != 0:
        blockers.append(f"unable to read GitHub Actions run {run_id}")
        return evidence

    data = json.loads(result.stdout)
    evidence.update(
        {
            "run_url": str(data.get("url") or ""),
            "workflow_name": str(data.get("workflowName") or ""),
            "run_status": str(data.get("status") or ""),
            "conclusion": str(data.get("conclusion") or ""),
            "head_sha": str(data.get("headSha") or ""),
        }
    )
    if evidence["run_status"] != "completed":
        blockers.append(f"run status is {evidence['run_status']}, expected completed")
    if evidence["conclusion"] != "success":
        blockers.append(f"run conclusion is {evidence['conclusion']}, expected success")
    if evidence["head_sha"] != expected_sha:
        blockers.append(f"run SHA {evidence['head_sha']} does not match current commit {expected_sha}")
    if f"/actions/runs/{run_id}" not in evidence["run_url"]:
        blockers.append("run URL does not contain run ID")
    return evidence


def compare_counts(src: dict, dst: dict) -> dict:
    mismatches: dict[str, dict[str, int | None]] = {}
    for table in KEY_TABLES:
        a = src["key_table_counts"].get(table)
        b = dst["key_table_counts"].get(table)
        if a != b:
            mismatches[table] = {"source": a, "restore": b}
    return mismatches


def pg_url_for_tool(url: str) -> str:
    """Add sslmode=require for Supabase/pooler URLs if not already set."""
    parsed = urlparse(url)
    if "sslmode" not in (parsed.query or ""):
        host = parsed.hostname or ""
        if "localhost" not in host and "127.0.0.1" not in host:
            url = url + ("&" if parsed.query else "?") + "sslmode=require"
    return url


def write_status(run_drill: bool = False) -> dict:
    blockers: list[str] = []
    commit = current_commit()
    accept = env("DB_ROLLBACK_ACCEPT") == "1"

    source_name, src_url = source_url()
    restore_name, dst_url = restore_url()

    if not valid_db_url(src_url):
        blockers.append("DB_ROLLBACK_SOURCE_DATABASE_URL is missing, placeholder, local, or invalid")
    if not valid_db_url(dst_url, allow_localhost=True):
        blockers.append("DB_ROLLBACK_RESTORE_DATABASE_URL is missing, placeholder, local, or invalid")
    if src_url and dst_url and src_url == dst_url:
        blockers.append("source and restore database URLs must differ")

    src_smoke = {"connected": False, "table_count": None, "alembic_version": "", "key_table_counts": {}, "blockers": []}
    dst_smoke = {"connected": False, "table_count": None, "alembic_version": "", "key_table_counts": {}, "blockers": []}
    dump_label = ""
    dump_hash = ""
    dump_size = 0
    backup_cmd = empty_command()
    restore_cmd = empty_command()
    mismatches: dict[str, dict[str, int | None]] = {}

    if not blockers:
        src_smoke = smoke(src_url)
        blockers.extend(f"source: {item}" for item in src_smoke["blockers"])

    if run_drill and not blockers:
        if shutil.which("pg_dump") is None:
            blockers.append("pg_dump is not installed")
        if shutil.which("pg_restore") is None:
            blockers.append("pg_restore is not installed")

    if run_drill and not blockers:
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        dump_path = WORK_DIR / f"db_rollback_{commit[:12]}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.dump"
        dump_label = dump_path.name

        backup = run(["pg_dump", "--format=custom", "--no-owner", "--no-acl", "--file", str(dump_path), pg_url_for_tool(src_url)])
        backup_cmd = command_evidence("pg_dump --format=custom --no-owner --no-acl --file <dump> <source-db>", backup)
        if backup.returncode != 0:
            blockers.append(f"backup command failed with exit code {backup.returncode}")

        if dump_path.exists():
            dump_size = dump_path.stat().st_size
            dump_hash = sha256(dump_path) if dump_size > 0 else ""
        if not dump_hash:
            blockers.append("backup dump was not created or was empty")

        if not blockers:
            restore = run(["pg_restore", "--clean", "--if-exists", "--no-owner", "--no-acl", "--dbname", dst_url, str(dump_path)])
            restore_cmd = command_evidence("pg_restore --clean --if-exists --no-owner --no-acl --dbname <restore-db> <dump>", restore)
            if restore.returncode != 0:
                blockers.append(f"restore command failed with exit code {restore.returncode}")

        if not blockers:
            dst_smoke = smoke(dst_url)
            blockers.extend(f"restore: {item}" for item in dst_smoke["blockers"])
            if src_smoke["table_count"] != dst_smoke["table_count"]:
                blockers.append(f"table count mismatch: source={src_smoke['table_count']}, restore={dst_smoke['table_count']}")
            if src_smoke["alembic_version"] != dst_smoke["alembic_version"]:
                blockers.append(f"alembic mismatch: source={src_smoke['alembic_version']}, restore={dst_smoke['alembic_version']}")
            mismatches = compare_counts(src_smoke, dst_smoke)
            if mismatches:
                blockers.append("key table count mismatches detected")
    elif not blockers and dst_url:
        dst_smoke = smoke(dst_url)
        mismatches = compare_counts(src_smoke, dst_smoke)

    if accept:
        if not run_drill and env("DB_ROLLBACK_ATTACH_ONLY") != "1":
            blockers.append("accepted evidence requires run_drill unless DB_ROLLBACK_ATTACH_ONLY=1")
        if not dump_hash or len(dump_hash) != 64:
            blockers.append("valid dump SHA256 checksum is required")
        if dump_size <= 0:
            blockers.append("non-empty dump size is required")
        if run_drill and restore_cmd["return_code"] is None:
            blockers.append("restore command did not run")
        run_evidence = gh_run(env("DB_ROLLBACK_RUN_ID"), commit)
        blockers.extend(run_evidence["blockers"])
    else:
        run_evidence = {"run_id": "", "run_url": "", "workflow_name": "", "run_status": "", "conclusion": "", "head_sha": "", "blockers": []}

    status = ACCEPTED if accept and not blockers else NOT_ACCEPTED
    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "current_commit": commit,
        "status": status,
        "source_db_url_label": db_label(src_url, source_name),
        "restore_db_url_label": db_label(dst_url, restore_name),
        "dump_file_label": dump_label,
        "dump_sha256": dump_hash,
        "dump_size_bytes": dump_size,
        "source_smoke": src_smoke,
        "restore_smoke": dst_smoke,
        "source_table_count": src_smoke["table_count"],
        "restore_table_count": dst_smoke["table_count"],
        "key_count_mismatches": mismatches,
        "backup_command": backup_cmd,
        "restore_command": restore_cmd,
        "github_run": run_evidence,
        "verified_by": "github-actions" if status == ACCEPTED else "unverified",
        "date_verified": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "blockers": blockers,
    }
    STATUS_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    write_markdown(out)
    return out


def write_markdown(status: dict) -> None:
    lines = [
        "# DB Backup / Restore / Rollback Evidence Status",
        "",
        f"Generated at: `{status['generated_at']}`",
        f"Commit: `{status['current_commit']}`",
        "",
        f"**Status:** `{status['status']}`",
        f"**Source DB:** `{status['source_db_url_label']}`",
        f"**Restore DB:** `{status['restore_db_url_label']}`",
        f"**Dump label:** `{status['dump_file_label']}`",
        f"**Dump SHA256:** `{status['dump_sha256']}`",
        f"**Dump size bytes:** `{status['dump_size_bytes']}`",
        f"**Source table count:** `{status['source_table_count']}`",
        f"**Restore table count:** `{status['restore_table_count']}`",
        f"**Source Alembic:** `{status['source_smoke']['alembic_version']}`",
        f"**Restore Alembic:** `{status['restore_smoke']['alembic_version']}`",
        f"**Run ID:** `{status['github_run']['run_id']}`",
        f"**Run URL:** `{status['github_run']['run_url']}`",
        "",
        "## Key table counts",
        "",
        "| Table | Source | Restore |",
        "|---|---:|---:|",
    ]
    tables = sorted(set(status["source_smoke"]["key_table_counts"]) | set(status["restore_smoke"]["key_table_counts"]))
    for table in tables:
        lines.append(f"| `{table}` | {status['source_smoke']['key_table_counts'].get(table)} | {status['restore_smoke']['key_table_counts'].get(table)} |")

    lines += ["", "## Key count mismatches", ""]
    if status["key_count_mismatches"]:
        for table, values in status["key_count_mismatches"].items():
            lines.append(f"- `{table}` source={values.get('source')} restore={values.get('restore')}")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Backup output excerpt",
        "",
        "```text",
        status["backup_command"]["output_excerpt"],
        "```",
        "",
        "## Restore output excerpt",
        "",
        "```text",
        status["restore_command"]["output_excerpt"],
        "```",
        "",
        "## Blockers",
        "",
    ]
    lines += [f"- {item}" for item in status["blockers"]] if status["blockers"] else ["- None"]
    lines += [
        "",
        "## No false-closure rules",
        "",
        "- DB-ROLLBACK-001 closes only in `DB_ROLLBACK_ACCEPT=1` mode.",
        "- Source and restore database URLs must differ.",
        "- Restore target must be disposable/staging, not production.",
        "- Dump is not uploaded; checksum and status evidence only are persisted.",
        "- Source and restore table count, Alembic version, and key table counts must match.",
        "- A successful GitHub Actions run matching current commit is required.",
        "- This proof does not close JWT, ARQ, DIAG-SCORE, AUDIT-WRITE, approvals, frontend runtime, image/SBOM, security scans, or beta release.",
        "",
    ]
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-drill", action="store_true")
    args = parser.parse_args()
    result = write_status(run_drill=args.run_drill)
    print(result["status"])
    print(f"dump_sha256={result['dump_sha256']}")
    print(f"dump_size_bytes={result['dump_size_bytes']}")
    print(f"source_table_count={result['source_table_count']}")
    print(f"restore_table_count={result['restore_table_count']}")
    if result["blockers"]:
        for item in result["blockers"]:
            print(f"- {item}")
        raise SystemExit(1)
