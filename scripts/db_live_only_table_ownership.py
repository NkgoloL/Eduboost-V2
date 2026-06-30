from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "docs/architecture/db_live_only_table_ownership.yml"
STATUS_JSON = ROOT / "docs/release/db_live_only_table_ownership_status.json"
STATUS_MD = ROOT / "docs/release/db_live_only_table_ownership_status.md"

EXPECTED_LIVE_ONLY_TABLES = [
    "consent_records",
    "data_export_requests",
    "erasure_requests",
    "correction_requests",
    "restriction_requests",
]

ALLOWED_OWNERSHIP = {
    "sql-owned",
    "orm-managed",
    "legacy-retired",
    "migration-required",
}


@dataclass(frozen=True)
class TableOwnershipRecord:
    table: str
    domain: str
    ownership: str
    reason: str
    orm_model_required: bool
    migration_action: str
    beta_blocking: bool
    orm_model_detected: bool
    accepted: bool
    blockers: list[str]


@dataclass(frozen=True)
class DbLiveOnlyTableOwnershipStatus:
    generated_at: str
    current_commit: str
    status: str
    policy_path: str
    expected_tables: list[str]
    records: list[TableOwnershipRecord]
    accepted_count: int
    required_count: int
    blockers: list[str]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def current_commit() -> str:
    result = _run(["git", "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _read_policy_text() -> str:
    return POLICY_PATH.read_text(encoding="utf-8") if POLICY_PATH.exists() else ""


def _yaml_value(block: str, key: str) -> str:
    match = re.search(rf"(?m)^    {re.escape(key)}:\s*(.*?)\s*$", block)
    return match.group(1).strip().strip('"').strip("'") if match else ""


def _yaml_bool(block: str, key: str) -> bool | None:
    value = _yaml_value(block, key).lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return None


def _table_block(policy_text: str, table: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(table)}:\n(.*?)(?=^  [a-zA-Z0-9_]+:\n|\Z)",
        policy_text,
    )
    return match.group(1) if match else ""


def _detect_orm_model(table: str) -> bool:
    candidates = list((ROOT / "app").rglob("*.py")) + list((ROOT / "backend").rglob("*.py")) if (ROOT / "backend").exists() else list((ROOT / "app").rglob("*.py"))
    patterns = [
        rf"__tablename__\s*=\s*['\"]{re.escape(table)}['\"]",
        rf"tablename\s*=\s*['\"]{re.escape(table)}['\"]",
        rf"Table\(\s*['\"]{re.escape(table)}['\"]",
    ]

    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(re.search(pattern, text) for pattern in patterns):
            return True

    return False


def build_records() -> list[TableOwnershipRecord]:
    policy_text = _read_policy_text()
    records: list[TableOwnershipRecord] = []

    for table in EXPECTED_LIVE_ONLY_TABLES:
        blockers: list[str] = []
        block = _table_block(policy_text, table)

        if not block:
            blockers.append("table missing from ownership policy")

        domain = _yaml_value(block, "domain")
        ownership = _yaml_value(block, "ownership")
        reason = _yaml_value(block, "reason")
        migration_action = _yaml_value(block, "migration_action")
        orm_model_required = _yaml_bool(block, "orm_model_required")
        beta_blocking = _yaml_bool(block, "beta_blocking")
        orm_model_detected = _detect_orm_model(table)

        if not domain:
            blockers.append("domain is missing")

        if ownership not in ALLOWED_OWNERSHIP:
            blockers.append(f"ownership must be one of {sorted(ALLOWED_OWNERSHIP)}")

        if not reason:
            blockers.append("reason is missing")

        if not migration_action:
            blockers.append("migration_action is missing")

        if orm_model_required is None:
            blockers.append("orm_model_required must be boolean")

        if beta_blocking is None:
            blockers.append("beta_blocking must be boolean")

        if ownership == "orm-managed" and not orm_model_detected:
            blockers.append("ownership is orm-managed but no ORM table declaration was detected")

        if ownership == "sql-owned" and orm_model_required is True:
            blockers.append("sql-owned table cannot require ORM model in this policy")

        if ownership == "migration-required" and beta_blocking is False:
            blockers.append("migration-required table must remain beta_blocking")

        accepted = not blockers

        records.append(
            TableOwnershipRecord(
                table=table,
                domain=domain,
                ownership=ownership,
                reason=reason,
                orm_model_required=bool(orm_model_required),
                migration_action=migration_action,
                beta_blocking=bool(beta_blocking),
                orm_model_detected=orm_model_detected,
                accepted=accepted,
                blockers=blockers,
            )
        )

    return records


def write_status() -> DbLiveOnlyTableOwnershipStatus:
    records = build_records()
    blockers: list[str] = []

    for record in records:
        blockers.extend(f"{record.table}: {blocker}" for blocker in record.blockers)

    accepted_count = sum(1 for record in records if record.accepted)
    required_count = len(EXPECTED_LIVE_ONLY_TABLES)

    status = (
        "db-live-only-table-ownership-accepted"
        if accepted_count == required_count and not blockers
        else "db-live-only-table-ownership-not-proven"
    )

    result = DbLiveOnlyTableOwnershipStatus(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status=status,
        policy_path=str(POLICY_PATH.relative_to(ROOT)),
        expected_tables=EXPECTED_LIVE_ONLY_TABLES,
        records=records,
        accepted_count=accepted_count,
        required_count=required_count,
        blockers=blockers,
    )

    STATUS_JSON.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    _write_markdown(result)
    return result


def _write_markdown(status: DbLiveOnlyTableOwnershipStatus) -> None:
    lines = [
        "# DB Live-Only Table Ownership Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        f"**Policy:** `{status.policy_path}`",
        f"**Accepted records:** `{status.accepted_count}/{status.required_count}`",
        "",
        "## Records",
        "",
        "| Table | Domain | Ownership | ORM model required | ORM model detected | Migration action | Beta blocking | Accepted |",
        "|---|---|---|---:|---:|---|---:|---:|",
    ]

    for record in status.records:
        lines.append(
            f"| `{record.table}` | `{record.domain}` | `{record.ownership}` | "
            f"{record.orm_model_required} | {record.orm_model_detected} | `{record.migration_action}` | "
            f"{record.beta_blocking} | {record.accepted} |"
        )

    lines.extend(["", "## Blockers", ""])
    if status.blockers:
        lines.extend(f"- {blocker}" for blocker in status.blockers)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## No false-closure rules",
            "",
            "- `sql-owned` means the table is documented as live SQL-owned and monitored, not ORM-managed.",
            "- This status does not add ORM models.",
            "- This status does not drop, rename, migrate, or backfill live tables.",
            "- This status does not prove audit writes, backup/restore/rollback, or legal approval.",
            "- If any table later becomes `migration-required`, it must become beta-blocking until migrated.",
            "",
        ]
    )

    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    result = write_status()
    print(result.status)
    print(f"{result.accepted_count}/{result.required_count}")
    if result.blockers:
        for blocker in result.blockers:
            print(f"- {blocker}")
        raise SystemExit(1)
