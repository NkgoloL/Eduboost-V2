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

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_HEAD = "20260708_2100_prd2_runtime_kg"
REQUIRED_TABLES = (
    "guardians",
    "learner_profiles",
    "assessments",
    "assessment_attempts",
    "diagnostic_items",
    "diagnostic_sessions",
    "study_plans",
    "lessons",
    "runtime_kg_nodes",
    "runtime_kg_edges",
    "runtime_kg_events",
    "ai_usage_events",
    "tutor_sessions",
    "audit_events",
)
REQUIRED_COLUMNS = {
    "diagnostic_items": (
        "irt_quality_state",
        "irt_discrimination",
        "irt_difficulty",
        "irt_guessing",
    )
}
STATIC_REQUIRED_FILES = (
    "alembic/versions/20260708_2100_prd2_runtime_kg_persistence.py",
    "scripts/generate_openapi.py",
    "scripts/generate_route_inventory.py",
    "app/modules/production_release/true_state_baseline.py",
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
    versions = root / "alembic" / "versions"
    if not versions.exists():
        return {"status": "fail", "reason": "missing alembic/versions"}
    present = sorted(path.stem for path in versions.glob("*.py"))
    matching = [name for name in present if name.startswith(REPOSITORY_HEAD)]
    return {
        "status": "pass" if matching else "fail",
        "expected_head_prefix": REPOSITORY_HEAD,
        "matching_revisions": matching,
        "revision_count": len(present),
    }


def _database_probe(root: Path) -> dict[str, Any]:
    url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")
    if not url:
        return {
            "status": "blocked",
            "reason": "DATABASE_URL not set; live database lineage and schema not proven",
            "expected_head": REPOSITORY_HEAD,
            "required_tables": list(REQUIRED_TABLES),
            "required_columns": REQUIRED_COLUMNS,
        }
    try:
        from sqlalchemy import create_engine, inspect, text
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"status": "blocked", "reason": f"sqlalchemy unavailable: {exc}"}
    try:  # pragma: no cover - requires live db
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            revisions = [row[0] for row in conn.execute(text("select version_num from alembic_version"))]
            inspector = inspect(conn)
            tables = set(inspector.get_table_names(schema="public"))
            missing_tables = [table for table in REQUIRED_TABLES if table not in tables]
            missing_columns: dict[str, list[str]] = {}
            for table, columns in REQUIRED_COLUMNS.items():
                if table not in tables:
                    missing_columns[table] = list(columns)
                    continue
                present = {col["name"] for col in inspector.get_columns(table, schema="public")}
                missing = [col for col in columns if col not in present]
                if missing:
                    missing_columns[table] = missing
        exact_head = revisions == [REPOSITORY_HEAD]
        clean = exact_head and not missing_tables and not missing_columns
        return {
            "status": "pass" if clean else "fail",
            "expected_head": REPOSITORY_HEAD,
            "live_revisions": revisions,
            "exact_repository_head": exact_head,
            "missing_tables": missing_tables,
            "missing_columns": missing_columns,
        }
    except Exception as exc:  # pragma: no cover - requires live db
        return {"status": "fail", "reason": str(exc), "expected_head": REPOSITORY_HEAD}


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


def collect_baseline(root: Path = ROOT, *, run_expensive_checks: bool = False) -> dict[str, Any]:
    checks = {
        "static_required_files": _static_files(root),
        "alembic_repository_graph": _alembic_graph(root),
        "database_lineage_and_schema": _database_probe(root),
        "redis_readiness_dependency": _redis_probe(),
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
