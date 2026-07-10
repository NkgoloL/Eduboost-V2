"""Collect PRD-11.0R true-state runtime baseline evidence.

The collector is intentionally fail-closed.  Missing infrastructure is recorded
as a blocker instead of being converted into a green readiness claim.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from app.core.runtime_readiness import (
    REQUIRED_RUNTIME_COLUMNS,
    REQUIRED_RUNTIME_TABLES,
    classify_database_lineage,
    load_alembic_revision_graph,
    validate_runtime_schema_contract,
)
from scripts.runtime.disposable_stack_lineage import verify_disposable_stack_lineage_contract

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COMPOSE_SERVICES = ("postgres", "redis", "api", "worker", "frontend")
STATIC_REQUIRED_FILES = (
    "alembic/versions/20260708_2100_prd2_runtime_kg_persistence.py",
    "scripts/generate_openapi.py",
    "scripts/generate_route_inventory.py",
    "scripts/runtime/verify_disposable_stack_schema_lineage.py",
    "app/modules/production_release/true_state_baseline.py",
    "app/core/runtime_readiness.py",
)


def _run(cmd: list[str], root: Path, timeout: int = 45) -> dict[str, Any]:
    try:
        completed = subprocess.run(
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
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
    except FileNotFoundError as exc:
        return {"status": "blocked", "reason": f"missing executable: {exc.filename}"}
    except subprocess.TimeoutExpired as exc:
        return {"status": "blocked", "reason": f"timeout after {timeout}s", "stdout_tail": (exc.stdout or "")[-1000:], "stderr_tail": (exc.stderr or "")[-1000:]}


def _static_files(root: Path) -> dict[str, Any]:
    missing = [path for path in STATIC_REQUIRED_FILES if not (root / path).exists()]
    return {"status": "pass" if not missing else "fail", "missing": missing}


def _alembic_graph(root: Path) -> dict[str, Any]:
    graph = load_alembic_revision_graph(root / "alembic" / "versions")
    return {
        "status": "pass" if graph.valid else "fail",
        "expected_single_head": graph.single_head,
        "repository_heads": list(graph.heads),
        "revision_count": len(graph.revisions),
        "version_file_count": len(graph.version_files),
    }


def _compose_service_contract(root: Path) -> dict[str, Any]:
    compose = root / "docker-compose.yml"
    if not compose.exists():
        return {"status": "fail", "reason": "missing docker-compose.yml", "expected_services": list(EXPECTED_COMPOSE_SERVICES)}
    text_value = compose.read_text()
    missing = [service for service in EXPECTED_COMPOSE_SERVICES if f"  {service}:" not in text_value]
    return {
        "status": "pass" if not missing else "fail",
        "expected_services": list(EXPECTED_COMPOSE_SERVICES),
        "missing_services": missing,
    }


def _database_probe(root: Path) -> dict[str, Any]:
    url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")
    graph = load_alembic_revision_graph(root / "alembic" / "versions")
    if not url:
        return {
            "status": "blocked",
            "reason": "DATABASE_URL not set; live database lineage and schema not proven",
            "expected_head": graph.single_head,
            "required_tables": list(REQUIRED_RUNTIME_TABLES),
            "required_columns": {table: list(columns) for table, columns in REQUIRED_RUNTIME_COLUMNS.items()},
        }
    try:
        from sqlalchemy import create_engine, text
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"status": "blocked", "reason": f"sqlalchemy unavailable: {exc}"}
    try:  # pragma: no cover - requires live db
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            revisions = [row[0] for row in conn.execute(text("select version_num from alembic_version order by version_num"))]
            table_rows = conn.execute(text("select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE'"))
            tables = {row[0] for row in table_rows}
            column_rows = conn.execute(text("select table_name, column_name from information_schema.columns where table_schema='public'"))
            columns: dict[str, set[str]] = {}
            for table, column in column_rows:
                columns.setdefault(str(table), set()).add(str(column))
        lineage = classify_database_lineage(revisions, graph)
        schema = validate_runtime_schema_contract(tables, columns)
        clean = lineage.get("status") == "ok" and schema.get("status") == "ok"
        return {
            "status": "pass" if clean else "fail",
            "lineage": lineage,
            "schema_contract": schema,
        }
    except Exception as exc:  # pragma: no cover - requires live db
        return {"status": "fail", "reason": str(exc), "expected_head": graph.single_head}


def _redis_probe() -> dict[str, Any]:
    url = os.getenv("REDIS_URL")
    if not url:
        return {"status": "blocked", "reason": "REDIS_URL not set; /ready Redis dependency not proven"}
    try:
        import redis
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"status": "blocked", "reason": f"redis client unavailable: {exc}"}
    try:  # pragma: no cover - requires live redis
        client = redis.from_url(url, socket_connect_timeout=2, socket_timeout=2)
        pong = client.ping()
        return {"status": "pass" if pong else "fail", "ping": bool(pong)}
    except Exception as exc:
        return {"status": "fail", "reason": str(exc)}


def _ready_http_probe() -> dict[str, Any]:
    base_url = os.getenv("API_BASE_URL") or os.getenv("EDUBOOST_API_BASE_URL")
    if not base_url:
        return {"status": "blocked", "reason": "API_BASE_URL not set; HTTP /ready not proven"}
    url = base_url.rstrip("/") + "/ready"
    try:  # pragma: no cover - requires live api
        with urlopen(url, timeout=5) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            status = response.getcode()
        return {"status": "pass" if status == 200 else "fail", "http_status": status, "url": url, "body_head": body[:1000]}
    except URLError as exc:  # pragma: no cover - requires live api
        return {"status": "fail", "url": url, "reason": str(exc)}
    except Exception as exc:  # pragma: no cover - requires live api
        return {"status": "fail", "url": url, "reason": f"{type(exc).__name__}: {exc}"}


def _generated_contracts(root: Path, run_checks: bool) -> dict[str, Any]:
    if not run_checks:
        return {"status": "blocked", "reason": "generated contract checks not executed in collector default mode"}
    openapi = _run(["python3", "scripts/generate_openapi.py", "--check"], root)
    routes = _run(["python3", "scripts/generate_route_inventory.py", "--check"], root)
    status = "pass" if openapi.get("status") == routes.get("status") == "pass" else "fail"
    return {"status": status, "openapi": openapi, "route_inventory": routes}


def _command_gate(name: str, command: list[str] | None, root: Path, run_checks: bool, timeout: int = 60) -> dict[str, Any]:
    if not run_checks or not command:
        return {"status": "blocked", "reason": f"{name} command not executed in collector default mode"}
    return _run(command, root, timeout=timeout)




def _disposable_stack_schema_lineage_reconciliation(root: Path) -> dict[str, Any]:
    result = verify_disposable_stack_lineage_contract(root, require_live=False)
    status = "pass" if result.get("contract_valid") is True and result.get("live_lineage_schema_green") is True else "blocked"
    if result.get("contract_valid") is not True:
        status = "fail"
    return {
        "status": status,
        "contract_valid": result.get("contract_valid") is True,
        "live_lineage_schema_green": result.get("live_lineage_schema_green") is True,
        "next_required_runtime_action": result.get("next_required_runtime_action"),
        "details": result,
    }

def collect_baseline(root: Path = ROOT, *, run_expensive_checks: bool = False) -> dict[str, Any]:
    checks = {
        "static_required_files": _static_files(root),
        "docker_compose_service_contract": _compose_service_contract(root),
        "alembic_repository_graph": _alembic_graph(root),
        "disposable_stack_schema_lineage_reconciliation": _disposable_stack_schema_lineage_reconciliation(root),
        "database_lineage_and_schema": _database_probe(root),
        "redis_readiness_dependency": _redis_probe(),
        "ready_http_probe": _ready_http_probe(),
        "generated_contracts": _generated_contracts(root, run_expensive_checks),
        "backend_unit_gate": _command_gate("backend_unit_gate", ["python3", "-m", "pytest", "tests/unit", "-q", "--no-cov"], root, run_expensive_checks, timeout=300),
        "integration_gate": _command_gate("integration_gate", ["python3", "-m", "pytest", "tests/integration", "-q", "--no-cov"], root, run_expensive_checks, timeout=300),
        "dependency_audit_gate": _command_gate("dependency_audit_gate", ["python3", "-m", "pip_audit", "-r", "requirements/base.txt"], root, run_expensive_checks, timeout=180),
        "frontend_quality_gate": _command_gate("frontend_quality_gate", ["bash", "-lc", "cd app/frontend && pnpm lint && pnpm test -- --run && pnpm build"], root, run_expensive_checks, timeout=300),
        "secret_baseline_gate": _command_gate("secret_baseline_gate", ["bash", "-lc", "detect-secrets scan --baseline .secrets.baseline app scripts .github >/tmp/prd110r_detect_secrets.json"], root, run_expensive_checks, timeout=180),
    }
    hard_gate_names = tuple(checks)
    blockers = [name for name, payload in checks.items() if payload.get("status") != "pass"]
    green = not blockers
    return {
        "prd_id": "PRD-11.0R",
        "collector_version": "prd11.0r/true-state-runtime-baseline/v1",
        "runtime_baseline_green": green,
        "overall_status": "green_runtime_baseline_restored" if green else "red_no_go_operational_hold_active",
        "operational_hold_required": not green,
        "hard_gate_names": list(hard_gate_names),
        "blockers": blockers,
        "checks": checks,
        "release_evidence_mode": "actual_probe_evidence_required_not_constant_status",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--run-expensive-checks", action="store_true")
    args = parser.parse_args()
    result = collect_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["runtime_baseline_green"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
