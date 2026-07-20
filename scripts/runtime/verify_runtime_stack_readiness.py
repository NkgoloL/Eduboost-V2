"""Verify PRD-11.0R runtime stack, DB lineage, and readiness contracts.

Default mode checks static/runtime-readiness contract installation. Use
``--require-live-green`` when a disposable stack is running and live readiness is
expected to be green.
"""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
import sys
from pathlib import Path
from typing import Any

from app.core.runtime_readiness import (
    load_alembic_revision_graph,
    validate_runtime_schema_contract,
)
from scripts.production_readiness.collect_prd1100r_true_state_runtime_baseline import (
    collect_baseline,
)

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COMPOSE_SERVICES = ("postgres", "redis", "api", "worker", "frontend")


def _compose_contract(root: Path) -> dict[str, Any]:
    compose = root / "docker-compose.yml"
    if not compose.exists():
        return {"valid": False, "missing_services": list(EXPECTED_COMPOSE_SERVICES)}
    text_value = compose.read_text()
    missing = [service for service in EXPECTED_COMPOSE_SERVICES if f"  {service}:" not in text_value]
    return {"valid": not missing, "missing_services": missing, "expected_services": list(EXPECTED_COMPOSE_SERVICES)}


def _health_contract(root: Path) -> dict[str, Any]:
    health = root / "app/core/health.py"
    text_value = health.read_text() if health.exists() else ""
    required_tokens = [
        "check_database_lineage_exact",
        "check_runtime_schema_contract",
        '"schema_contract": await check_schema_contract()',
    ]
    missing = [token for token in required_tokens if token not in text_value]
    return {"valid": not missing, "missing_tokens": missing}


def _py_compile(root: Path) -> dict[str, Any]:
    cmd = [
        sys.executable,
        "-m",
        "py_compile",
        "app/core/runtime_readiness.py",
        "app/core/health.py",
        "scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py",
        "scripts/runtime/verify_runtime_stack_readiness.py",
    ]
    completed = run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {
        "valid": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def verify_contract(root: Path = ROOT, *, require_live_green: bool = False) -> dict[str, Any]:
    graph = load_alembic_revision_graph(root / "alembic" / "versions")
    baseline = collect_baseline(root, run_expensive_checks=False)
    schema_contract = validate_runtime_schema_contract(
        present_tables=set(__import__("app.core.runtime_readiness").core.runtime_readiness.REQUIRED_RUNTIME_TABLES),
        present_columns={
            table: tuple(columns)
            for table, columns in __import__("app.core.runtime_readiness").core.runtime_readiness.REQUIRED_RUNTIME_COLUMNS.items()
        },
    )
    checks = {
        "py_compile": _py_compile(root),
        "compose_contract": _compose_contract(root),
        "health_contract": _health_contract(root),
        "alembic_single_head": {"valid": graph.valid, "heads": list(graph.heads), "revision_count": len(graph.revisions)},
        "orm_schema_contract": {"valid": schema_contract.get("status") == "ok", **schema_contract},
        "baseline_collector_contract": {
            "valid": baseline.get("release_evidence_mode") == "actual_probe_evidence_required_not_constant_status"
            and "database_lineage_and_schema" in baseline.get("hard_gate_names", [])
            and "ready_http_probe" in baseline.get("hard_gate_names", []),
            "hard_gate_names": baseline.get("hard_gate_names", []),
            "runtime_baseline_green": baseline.get("runtime_baseline_green"),
            "blockers": baseline.get("blockers", []),
        },
    }
    contract_valid = all(payload.get("valid") is True for payload in checks.values())
    live_green = bool(baseline.get("runtime_baseline_green"))
    valid = contract_valid and (live_green if require_live_green else True)
    return {
        "valid": valid,
        "contract_valid": contract_valid,
        "live_green_required": require_live_green,
        "runtime_baseline_green": live_green,
        "checks": checks,
        "baseline_snapshot": baseline,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-live-green", action="store_true")
    args = parser.parse_args()
    result = verify_contract(ROOT, require_live_green=args.require_live_green)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
