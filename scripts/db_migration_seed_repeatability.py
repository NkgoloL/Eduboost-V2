from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "temp/db_repeatability"
RAW_SQL = OUT_DIR / "alembic_upgrade_head.raw.sql"
SUPABASE_SQL = OUT_DIR / "alembic_upgrade_head.supabase.sql"
IRT_SEED_SQL = OUT_DIR / "seed_irt_items.sql"

STATUS_JSON = ROOT / "docs/release/db_migration_seed_repeatability_status.json"
STATUS_MD = ROOT / "docs/release/db_migration_seed_repeatability_status.md"

EXPECTED_HEAD = "20260516_0100"
EXPECTED_IRT_ROWS = 1600

REQUIRED_TABLES = [
    "audit_events",
    "audit_logs",
    "calibration_audits",
    "diagnostic_items",
    "diagnostic_sessions",
    "guardians",
    "irt_items",
    "item_exposures",
    "knowledge_gaps",
    "learner_profiles",
    "lesson_feedback",
    "lessons",
    "mastery_snapshots",
    "parental_consents",
    "practice_queue",
    "rlhf_exports",
    "spaced_review_schedule",
    "stripe_webhook_events",
    "subject_mastery",
    "topic_mastery",
]

CHATTER_PREFIXES = (
    "DEBUG:",
    "INFO [",
    "Place this file at:",
    "====",
    "Task ",
)

BROKEN_NULL_IRT_SEED_RE = re.compile(
    r"""INSERT INTO irt_items \(
 id, grade, subject, topic, language, question_text, options,
 correct_option, a_param, b_param
 \)
 VALUES \(
 NULL, NULL, NULL, NULL, NULL, NULL,
 CAST\(NULL AS JSONB\), NULL, NULL, NULL
 \)
 ON CONFLICT \(id\) DO NOTHING;\n\n""",
    flags=re.MULTILINE,
)


@dataclass(frozen=True)
class DbRepeatabilityStatus:
    generated_at: str
    current_commit: str
    status: str
    raw_sql_path: str
    supabase_sql_path: str
    irt_seed_sql_path: str
    alembic_head_present: bool
    required_tables_present: dict[str, bool]
    raw_sql_line_count: int
    supabase_sql_line_count: int
    removed_chatter_lines: int
    removed_null_seed_blocks: int
    removed_supabase_role_lines: int
    generated_irt_seed_rows: int
    unique_irt_seed_rows: int
    blockers: list[str]


def _run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def current_commit() -> str:
    result = _run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def generate_raw_alembic_sql() -> tuple[bool, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    env = {
        **__import__("os").environ,
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/eduboost",
    }
    alembic_path = ROOT / ".venv" / "bin" / "alembic"
    result = _run([str(alembic_path), "upgrade", "head", "--sql"], env=env)
    RAW_SQL.write_text(result.stdout, encoding="utf-8")
    return result.returncode == 0, result.stdout





def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load migration module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def generate_irt_seed_sql() -> tuple[int, int]:
    migration_paths = [
        ROOT / "alembic/versions/0005_seed_irt_items.py",
        ROOT / "alembic/versions/0007_caps_irt_item_bank.py",
    ]

    rows: list[dict[str, Any]] = []
    for path in migration_paths:
        module = _load_module(path)
        rows.extend(module._generate_items())

    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        row_id = str(row["id"])
        if row_id not in seen:
            seen.add(row_id)
            unique.append(row)

    lines = ["BEGIN;"]
    for row in unique:
        values = [
            _sql_literal(row["id"]),
            _sql_literal(row["grade"]),
            _sql_literal(row["subject"]),
            _sql_literal(row["topic"]),
            _sql_literal(row["language"]),
            _sql_literal(row["question_text"]),
            _sql_literal(row["options"]) + "::jsonb",
            _sql_literal(row["correct_option"]),
            _sql_literal(row["a_param"]),
            _sql_literal(row["b_param"]),
        ]
        lines.append(
            "INSERT INTO public.irt_items "
            "(id, grade, subject, topic, language, question_text, options, correct_option, a_param, b_param) "
            f"VALUES ({', '.join(values)}) ON CONFLICT (id) DO NOTHING;"
        )
    lines.append("COMMIT;")

    IRT_SEED_SQL.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows), len(unique)





def write_status() -> DbRepeatabilityStatus:
    blockers: list[str] = []

    raw_ok, raw_output = generate_raw_alembic_sql()
    if not raw_ok:
        blockers.append("alembic upgrade head --sql failed")

    cleaned, removed_chatter, removed_null_blocks, removed_role_lines = clean_supabase_sql(raw_output)
    SUPABASE_SQL.write_text(cleaned, encoding="utf-8")

    generated_rows, unique_rows = generate_irt_seed_sql()

    alembic_head_present = EXPECTED_HEAD in cleaned
    table_presence = _required_table_presence(cleaned)

    if not alembic_head_present:
        blockers.append(f"expected Alembic head {EXPECTED_HEAD} missing from generated SQL")

    missing_tables = [table for table, present in table_presence.items() if not present]
    if missing_tables:
        blockers.append("required runtime table DDL missing: " + ", ".join(missing_tables))

    if "DEBUG:" in cleaned or "INFO [" in cleaned:
        blockers.append("generated Supabase SQL still contains non-SQL chatter")

    if "CAST(NULL AS JSONB)" in cleaned:
        blockers.append("generated Supabase SQL still contains broken null IRT seed rows")

    if "eduboost_app" in cleaned:
        blockers.append("generated Supabase SQL still references missing Supabase role eduboost_app")

    if unique_rows != EXPECTED_IRT_ROWS:
        blockers.append(f"expected {EXPECTED_IRT_ROWS} unique IRT seed rows, generated {unique_rows}")

    if "ON CONFLICT (id) DO NOTHING" not in IRT_SEED_SQL.read_text(encoding="utf-8"):
        blockers.append("IRT seed SQL is not idempotent")

    status = "db-migration-seed-repeatability-passing" if not blockers else "db-migration-seed-repeatability-not-proven"

    result = DbRepeatabilityStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status=status,
        raw_sql_path=str(RAW_SQL.relative_to(ROOT)),
        supabase_sql_path=str(SUPABASE_SQL.relative_to(ROOT)),
        irt_seed_sql_path=str(IRT_SEED_SQL.relative_to(ROOT)),
        alembic_head_present=alembic_head_present,
        required_tables_present=table_presence,
        raw_sql_line_count=len(raw_output.splitlines()),
        supabase_sql_line_count=len(cleaned.splitlines()),
        removed_chatter_lines=removed_chatter,
        removed_null_seed_blocks=removed_null_blocks,
        removed_supabase_role_lines=removed_role_lines,
        generated_irt_seed_rows=generated_rows,
        unique_irt_seed_rows=unique_rows,
        blockers=blockers,
    )

    STATUS_JSON.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    _write_markdown(result)
    return result


def _write_markdown(status: DbRepeatabilityStatus) -> None:
    lines = [
        "# DB Migration + Seed Repeatability Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Raw Alembic SQL:** `{status.raw_sql_path}`",
        f"**Supabase SQL:** `{status.supabase_sql_path}`",
        f"**IRT seed SQL:** `{status.irt_seed_sql_path}`",
        "",
        "## Summary",
        "",
        f"- Alembic head `{EXPECTED_HEAD}` present: `{status.alembic_head_present}`",
        f"- Raw SQL lines: `{status.raw_sql_line_count}`",
        f"- Supabase SQL lines: `{status.supabase_sql_line_count}`",
        f"- Removed chatter lines: `{status.removed_chatter_lines}`",
        f"- Removed broken null seed blocks: `{status.removed_null_seed_blocks}`",
        f"- Removed Supabase role lines: `{status.removed_supabase_role_lines}`",
        f"- Generated IRT seed rows: `{status.generated_irt_seed_rows}`",
        f"- Unique IRT seed rows: `{status.unique_irt_seed_rows}`",
        "",
        "## Required runtime tables",
        "",
        "| Table | DDL present |",
        "|---|---:|",
    ]

    for table, present in status.required_tables_present.items():
        lines.append(f"| `{table}` | {present} |")

    lines.extend(["", "## Apply commands", ""])
    lines.extend(
        [
            "```bash",
            "# Generate checked SQL artifacts",
            "make db-migration-seed-repeatability-status",
            "",
            "# Apply manually to linked Supabase after review",
            "npx --yes supabase db query --linked --file temp/db_repeatability/alembic_upgrade_head.supabase.sql",
            "npx --yes supabase db query --linked --file temp/db_repeatability/seed_irt_items.sql",
            "```",
            "",
            "## Blockers",
            "",
        ]
    )

    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- This proves repeatable generation of Supabase-safe migration and IRT seed SQL.",
            "- It does not prove remote apply unless the generated SQL is applied and verified separately.",
            "- It does not decide whether `diagnostic_items` should be populated.",
            "- It does not decide ownership of live-only POPIA/DSR tables.",
            "- It does not prove audit writes or backup/restore/rollback posture.",
            "",
        ]
    )

    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")




# DB_REPEATABILITY_OVERRIDE_FIX_V1
def clean_supabase_sql(raw_sql: str) -> tuple[str, int, int, int]:
    lines: list[str] = []
    removed_chatter = 0
    removed_role_lines = 0

    for line in raw_sql.splitlines():
        stripped = line.strip()
        if stripped.startswith(CHATTER_PREFIXES):
            removed_chatter += 1
            continue
        if 'eduboost_app' in line:
            removed_role_lines += 1
            continue
        lines.append(line)

    cleaned = '\n'.join(lines) + '\n'

    broken_null_seed = re.compile(
        r'INSERT\s+INTO\s+(?:public\.)?"?irt_items"?\s*\('
        r'.*?CAST\s*\(\s*NULL\s+AS\s+JSONB\s*\)'
        r'.*?\)\s*ON\s+CONFLICT\s*\(\s*id\s*\)'
        r'\s*DO\s+NOTHING\s*;',
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned, removed_null_blocks = broken_null_seed.subn('', cleaned)

    return cleaned, removed_chatter, removed_null_blocks, removed_role_lines


def _required_table_presence(sql: str) -> dict[str, bool]:
    result: dict[str, bool] = {}
    for table in REQUIRED_TABLES:
        pattern = re.compile(
            rf'create\s+table\s+(?:if\s+not\s+exists\s+)?'
            rf'(?:(?:public|"public")\s*\.\s*)?'
            rf'"?{re.escape(table)}"?\s*\(',
            flags=re.IGNORECASE,
        )
        result[table] = bool(pattern.search(sql))
    return result

if __name__ == "__main__":
    result = write_status()
    print(result.status)
    print(result.unique_irt_seed_rows)
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
        raise SystemExit(1)
