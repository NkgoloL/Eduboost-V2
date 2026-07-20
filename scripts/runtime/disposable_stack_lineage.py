"""Disposable stack and schema-lineage reconciliation helpers for PRD-11.0R restore work.

This module deliberately separates *contract installation* from *live proof*.
Static contract checks can pass in CI without a running stack, but live proof is
blocked until a disposable PostgreSQL/Redis/API/worker/frontend stack is running
and the live database revision exactly matches the repository Alembic head.
"""
from __future__ import annotations

import argparse
import json
import os
from scripts._subprocess import run
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.runtime_readiness import (
    REQUIRED_RUNTIME_COLUMNS,
    REQUIRED_RUNTIME_TABLES,
    classify_database_lineage,
    load_alembic_revision_graph,
    validate_runtime_schema_contract,
)

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_DISPOSABLE_STACK_SERVICES = ("postgres", "redis", "api", "worker", "frontend")
LINEAGE_RECONCILIATION_BLOCKERS = (
    "unknown_live_alembic_revision",
    "missing_or_base_only_live_revision",
    "live_database_not_at_repository_head",
    "critical_runtime_schema_contract_missing",
)
NON_NEGOTIABLE_POLICY_FLAGS = {
    "no_blind_alembic_stamp": True,
    "snapshot_before_lineage_repair": True,
    "fresh_disposable_database_must_migrate_to_head": True,
    "existing_database_requires_inventory_before_bridge_or_rebuild": True,
    "runtime_schema_contract_required_after_migration": True,
    "ready_probe_required_after_stack_start": True,
}


@dataclass(frozen=True)
class LineageProbeConfig:
    """Runtime lineage probe configuration."""

    database_url: str | None = None
    api_base_url: str | None = None
    redis_url: str | None = None
    docker_compose_file: str = "docker-compose.yml"


def _run(cmd: list[str], root: Path, timeout: int = 60) -> dict[str, Any]:
    try:
        completed = run(
            cmd,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "status": "pass" if completed.returncode == 0 else "fail",
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-3000:],
            "stderr_tail": completed.stderr[-3000:],
        }
    except FileNotFoundError as exc:
        return {"status": "blocked", "reason": f"missing executable: {exc.filename}"}
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "blocked",
            "reason": f"timeout after {timeout}s",
            "stdout_tail": (exc.stdout or "")[-1000:],
            "stderr_tail": (exc.stderr or "")[-1000:],
        }


def build_disposable_stack_commands(compose_file: str = "docker-compose.yml") -> dict[str, Any]:
    """Return the canonical command plan for disposable-stack proof."""

    return {
        "compose_file": compose_file,
        "commands": [
            {"step": "start_stack", "command": f"docker compose -f {compose_file} up -d postgres redis api worker frontend"},
            {"step": "apply_migrations", "command": "alembic upgrade head"},
            {"step": "verify_lineage_schema", "command": "PYTHONPATH=. python3 scripts/runtime/verify_disposable_stack_schema_lineage.py --require-live --json"},
            {"step": "probe_ready", "command": "curl -fsS ${API_BASE_URL:-http://localhost:8000}/ready"},
            {"step": "capture_baseline", "command": "PYTHONPATH=. python3 scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py --run-expensive-checks --json"},
        ],
        "policy": NON_NEGOTIABLE_POLICY_FLAGS,
    }


def verify_compose_file_contract(root: Path = ROOT, compose_file: str = "docker-compose.yml") -> dict[str, Any]:
    path = root / compose_file
    if not path.exists():
        return {"valid": False, "status": "fail", "missing_compose_file": compose_file, "expected_services": list(EXPECTED_DISPOSABLE_STACK_SERVICES)}
    text = path.read_text()
    missing = [service for service in EXPECTED_DISPOSABLE_STACK_SERVICES if f"  {service}:" not in text]
    return {
        "valid": not missing,
        "status": "pass" if not missing else "fail",
        "compose_file": compose_file,
        "expected_services": list(EXPECTED_DISPOSABLE_STACK_SERVICES),
        "missing_services": missing,
    }


def verify_migration_graph_contract(root: Path = ROOT) -> dict[str, Any]:
    graph = load_alembic_revision_graph(root / "alembic" / "versions")
    return {
        "valid": graph.valid,
        "status": "pass" if graph.valid else "fail",
        "expected_single_head": graph.single_head,
        "repository_heads": list(graph.heads),
        "revision_count": len(graph.revisions),
    }


def verify_runtime_schema_contract_static() -> dict[str, Any]:
    schema = validate_runtime_schema_contract(
        present_tables=set(REQUIRED_RUNTIME_TABLES),
        present_columns={table: tuple(columns) for table, columns in REQUIRED_RUNTIME_COLUMNS.items()},
    )
    return {"valid": schema.get("status") == "ok", **schema}


def live_database_lineage_schema_probe(database_url: str | None, root: Path = ROOT) -> dict[str, Any]:
    """Probe a live DB if DATABASE_URL is supplied; otherwise return blocked."""

    graph = load_alembic_revision_graph(root / "alembic" / "versions")
    if not database_url:
        return {
            "status": "blocked",
            "reason": "DATABASE_URL not set; disposable/existing database lineage not proven",
            "expected_repository_head": graph.single_head,
            "policy": NON_NEGOTIABLE_POLICY_FLAGS,
        }
    try:
        from sqlalchemy import create_engine, text
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"status": "blocked", "reason": f"sqlalchemy unavailable: {exc}"}
    try:  # pragma: no cover - requires live database
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            revisions = [str(row[0]) for row in conn.execute(text("select version_num from alembic_version order by version_num"))]
            table_rows = conn.execute(text("select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE'"))
            tables = {str(row[0]) for row in table_rows}
            column_rows = conn.execute(text("select table_name, column_name from information_schema.columns where table_schema='public'"))
            columns: dict[str, set[str]] = {}
            for table, column in column_rows:
                columns.setdefault(str(table), set()).add(str(column))
        lineage = classify_database_lineage(revisions, graph)
        schema = validate_runtime_schema_contract(tables, columns)
        clean = lineage.get("status") == "ok" and schema.get("status") == "ok"
        mode = "exact_head_verified" if clean else "lineage_or_schema_reconciliation_required"
        return {"status": "pass" if clean else "fail", "reconciliation_mode": mode, "lineage": lineage, "schema_contract": schema}
    except Exception as exc:  # pragma: no cover - requires live database
        return {"status": "fail", "reason": str(exc), "expected_repository_head": graph.single_head}


def build_lineage_reconciliation_decision(live_probe: dict[str, Any]) -> dict[str, Any]:
    """Classify the safe reconciliation path without mutating a database."""

    status = live_probe.get("status")
    if status == "pass":
        return {
            "status": "pass",
            "decision": "lineage_and_schema_already_at_repository_head",
            "safe_next_action": "run_full_runtime_baseline_and_ready_probe",
            "blind_stamp_allowed": False,
        }
    if status == "blocked":
        return {
            "status": "blocked",
            "decision": "live_database_not_available_for_reconciliation",
            "safe_next_action": "start_disposable_stack_or_provide_DATABASE_URL_before claiming lineage proof",
            "blind_stamp_allowed": False,
        }
    lineage = live_probe.get("lineage") if isinstance(live_probe.get("lineage"), dict) else {}
    schema = live_probe.get("schema_contract") if isinstance(live_probe.get("schema_contract"), dict) else {}
    unknown = bool(lineage.get("unknown_revisions"))
    schema_missing = bool(schema.get("missing_tables") or schema.get("missing_columns"))
    if unknown:
        safe = "snapshot_and_inventory_existing_database_then_choose explicit bridge migration or rebuild disposable canonical DB"
    elif schema_missing:
        safe = "apply missing migrations on disposable clone then compare schema before touching existing data"
    else:
        safe = "run alembic upgrade head on disposable clone and re-probe readiness"
    return {
        "status": "fail",
        "decision": "lineage_reconciliation_required",
        "unknown_live_revision": unknown,
        "schema_contract_missing": schema_missing,
        "safe_next_action": safe,
        "blind_stamp_allowed": False,
    }


def verify_disposable_stack_lineage_contract(
    root: Path = ROOT,
    *,
    require_live: bool = False,
    config: LineageProbeConfig | None = None,
) -> dict[str, Any]:
    """Verify restore-2 stack/lineage contract installation and optional live proof."""

    config = config or LineageProbeConfig(
        database_url=os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI"),
        api_base_url=os.getenv("API_BASE_URL") or os.getenv("EDUBOOST_API_BASE_URL"),
        redis_url=os.getenv("REDIS_URL"),
    )
    live_probe = live_database_lineage_schema_probe(config.database_url, root)
    decision = build_lineage_reconciliation_decision(live_probe)
    commands = build_disposable_stack_commands(config.docker_compose_file)
    checks = {
        "compose_contract": verify_compose_file_contract(root, config.docker_compose_file),
        "migration_graph_contract": verify_migration_graph_contract(root),
        "runtime_schema_contract_static": verify_runtime_schema_contract_static(),
        "lineage_probe": live_probe,
        "lineage_reconciliation_decision": decision,
        "disposable_stack_command_plan": {"valid": True, **commands},
        "policy": {"valid": all(NON_NEGOTIABLE_POLICY_FLAGS.values()), **NON_NEGOTIABLE_POLICY_FLAGS},
    }
    contract_valid = all(
        checks[name].get("valid") is True
        for name in (
            "compose_contract",
            "migration_graph_contract",
            "runtime_schema_contract_static",
            "disposable_stack_command_plan",
            "policy",
        )
    )
    live_valid = live_probe.get("status") == "pass"
    valid = contract_valid and (live_valid if require_live else True)
    return {
        "valid": valid,
        "contract_valid": contract_valid,
        "live_lineage_schema_required": require_live,
        "live_lineage_schema_green": live_valid,
        "checks": checks,
        "next_required_runtime_action": "provide live disposable stack evidence" if not live_valid else "run full true-state baseline with expensive checks",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()
    result = verify_disposable_stack_lineage_contract(ROOT, require_live=args.require_live)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
