"""Runtime stack, database lineage, schema, and /ready green evidence.

PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5 is the first execution slice that
requires *live runtime proof* instead of another static contract.  The command
runner in this module captures independent outputs for the disposable stack,
Alembic/schema lineage, Redis, and the HTTP /ready endpoint.  It is fail-closed:
when a live stack is absent, evidence is recorded as blocked/red, not accepted.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "var/prd11/runtime-restore/execution-5/runtime-stack-db-ready-green"

REQUIRED_GREEN_GATES = (
    "compose_contract",
    "alembic_upgrade_head",
    "disposable_stack_schema_lineage_live",
    "redis_readiness",
    "ready_http_probe",
)


@dataclass(frozen=True)
class RuntimeGreenCommand:
    gate_id: str
    description: str
    command: list[str] | None
    artifact: str
    release_blocking: bool = True
    requires_live_stack: bool = True
    requires_positive_path: bool = True
    requires_failure_mode: bool = True


def _api_base_url() -> str:
    return os.getenv("API_BASE_URL") or os.getenv("EDUBOOST_API_BASE_URL") or "http://localhost:8000"


def _command_plan() -> list[RuntimeGreenCommand]:
    return [
        RuntimeGreenCommand(
            gate_id="compose_contract",
            description="Verify committed disposable-stack service contract for postgres, redis, api, worker, and frontend.",
            command=[sys.executable, "scripts/runtime/verify_runtime_stack_readiness.py", "--json"],
            artifact="compose-contract.json",
            requires_live_stack=False,
        ),
        RuntimeGreenCommand(
            gate_id="alembic_upgrade_head",
            description="Apply migrations to the disposable database and prove the migration command succeeds.",
            command=[sys.executable, "-m", "alembic", "upgrade", "head"],
            artifact="alembic-upgrade-head.json",
        ),
        RuntimeGreenCommand(
            gate_id="disposable_stack_schema_lineage_live",
            description="Verify live DB revision equals repository Alembic head and critical runtime schema exists.",
            command=[sys.executable, "scripts/runtime/verify_disposable_stack_schema_lineage.py", "--require-live", "--json"],
            artifact="disposable-stack-schema-lineage-live.json",
        ),
        RuntimeGreenCommand(
            gate_id="redis_readiness",
            description="Ping the configured Redis instance from the current repo environment.",
            command=None,
            artifact="redis-readiness.json",
        ),
        RuntimeGreenCommand(
            gate_id="ready_http_probe",
            description="Probe API /ready and require HTTP 200 from the live API.",
            command=None,
            artifact="ready-http-probe.json",
        ),
    ]


def command_plan() -> list[dict[str, Any]]:
    return [asdict(command) for command in _command_plan()]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_command(command: list[str], root: Path, *, timeout: int = 300) -> dict[str, Any]:
    started = time.time()
    try:
        completed = subprocess.run(
            command,
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
            "command": command,
            "duration_seconds": round(time.time() - started, 3),
            "stdout_tail": completed.stdout[-5000:],
            "stderr_tail": completed.stderr[-5000:],
        }
    except FileNotFoundError as exc:
        return {"status": "blocked", "command": command, "reason": f"missing executable: {exc.filename}"}
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "blocked",
            "command": command,
            "reason": f"timeout after {timeout}s",
            "stdout_tail": (exc.stdout or "")[-2000:],
            "stderr_tail": (exc.stderr or "")[-2000:],
        }


def _redis_probe() -> dict[str, Any]:
    redis_url = os.getenv("REDIS_URL") or os.getenv("EDUBOOST_REDIS_URL")
    if not redis_url:
        return {"status": "blocked", "reason": "REDIS_URL or EDUBOOST_REDIS_URL not set"}
    try:
        import redis  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"status": "blocked", "reason": f"redis package unavailable: {exc}"}
    try:  # pragma: no cover - requires live redis
        client = redis.from_url(redis_url, socket_connect_timeout=5, socket_timeout=5)
        pong = client.ping()
        return {"status": "pass" if pong else "fail", "redis_url_present": True, "ping": bool(pong)}
    except Exception as exc:  # noqa: BLE001  # pragma: no cover - requires live redis
        return {"status": "fail", "redis_url_present": True, "reason": f"{type(exc).__name__}: {exc}"}


def _ready_probe() -> dict[str, Any]:
    url = _api_base_url().rstrip("/") + "/ready"
    request = Request(url, headers={"Accept": "application/json"})
    try:  # pragma: no cover - requires live api
        with urlopen(request, timeout=15) as response:  # noqa: S310 - configured local/staging probe URL
            body = response.read().decode("utf-8", errors="replace")
            status_code = getattr(response, "status", 200)
        parsed: Any
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw_body_tail": body[-1000:]}
        return {
            "status": "pass" if status_code == 200 else "fail",
            "url": url,
            "http_status": status_code,
            "json": parsed,
        }
    except HTTPError as exc:  # pragma: no cover - requires live api
        body = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
        return {"status": "fail", "url": url, "http_status": exc.code, "body_tail": body[-2000:]}
    except URLError as exc:  # pragma: no cover - requires live api
        return {"status": "fail", "url": url, "reason": str(exc)}
    except Exception as exc:  # noqa: BLE001  # pragma: no cover - requires live api
        return {"status": "fail", "url": url, "reason": f"{type(exc).__name__}: {exc}"}


def _gate_passed(gate_id: str, payload: dict[str, Any]) -> bool:
    if gate_id == "compose_contract":
        return payload.get("status") == "pass" or payload.get("valid") is True or payload.get("contract_valid") is True
    return payload.get("status") == "pass" or payload.get("valid") is True


def run_runtime_stack_db_ready_green(
    root: Path = ROOT,
    *,
    execute: bool = False,
    apply_migrations: bool = False,
    require_green: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Run or list the runtime stack green evidence commands."""

    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []

    if not execute:
        return {
            "schema_version": "prd11.0r/runtime-restore-execution-5/runtime-stack-db-ready-green/v1",
            "execute": False,
            "all_green": False,
            "require_green": require_green,
            "command_plan": command_plan(),
            "blockers": ["runtime_green_commands_not_executed"],
            "output_dir": str(output_dir),
        }

    for item in _command_plan():
        if item.gate_id == "alembic_upgrade_head" and not apply_migrations:
            payload = {
                "status": "blocked",
                "reason": "--apply-migrations was not supplied; refusing to claim fresh disposable DB migration proof",
                "command": item.command,
            }
        elif item.gate_id == "redis_readiness":
            payload = _redis_probe()
        elif item.gate_id == "ready_http_probe":
            payload = _ready_probe()
        elif item.command is not None:
            timeout = 600 if item.gate_id == "alembic_upgrade_head" else 300
            payload = _run_command(item.command, root, timeout=timeout)
        else:  # defensive only
            payload = {"status": "blocked", "reason": "no command or probe configured"}
        results[item.gate_id] = payload
        _write_json(output_dir / item.artifact, payload)
        if item.gate_id in REQUIRED_GREEN_GATES and not _gate_passed(item.gate_id, payload):
            blockers.append(item.gate_id)

    all_green = not blockers
    summary = {
        "schema_version": "prd11.0r/runtime-restore-execution-5/runtime-stack-db-ready-green/v1",
        "execute": True,
        "require_green": require_green,
        "all_green": all_green,
        "runtime_stack_green": all_green,
        "database_lineage_green": _gate_passed("disposable_stack_schema_lineage_live", results.get("disposable_stack_schema_lineage_live", {})),
        "schema_contract_green": _gate_passed("disposable_stack_schema_lineage_live", results.get("disposable_stack_schema_lineage_live", {})),
        "redis_readiness_green": _gate_passed("redis_readiness", results.get("redis_readiness", {})),
        "ready_probe_green": _gate_passed("ready_http_probe", results.get("ready_http_probe", {})),
        "alembic_upgrade_head_green": _gate_passed("alembic_upgrade_head", results.get("alembic_upgrade_head", {})),
        "blockers": blockers,
        "command_plan": command_plan(),
        "results": results,
        "output_dir": str(output_dir),
    }
    _write_json(output_dir / "summary.json", summary)
    return summary


def load_runtime_green_summary(root: Path = ROOT, *, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    path = output_dir if output_dir.is_absolute() else root / output_dir
    summary = path / "summary.json"
    return json.loads(summary.read_text()) if summary.exists() else {}


def evaluate_runtime_green_contract(root: Path = ROOT, *, require_green: bool = False) -> dict[str, Any]:
    helper = root / "scripts/runtime/runtime_stack_db_ready_green.py"
    runner = root / "scripts/runtime/run_runtime_stack_db_ready_green.py"
    verifier = root / "scripts/runtime/verify_runtime_stack_db_ready_green.py"
    source = helper.read_text() if helper.exists() else ""
    summary = load_runtime_green_summary(root)
    checks = {
        "helper_exists": helper.exists(),
        "runner_exists": runner.exists(),
        "verifier_exists": verifier.exists(),
        "uses_current_python_interpreter": "sys.executable" in source and "verify_disposable_stack_schema_lineage.py" in source,
        "requires_alembic_upgrade_proof": "--apply-migrations" in source and "alembic_upgrade_head" in source,
        "requires_redis_probe": "redis_readiness" in source and "REDIS_URL" in source,
        "requires_ready_probe": "ready_http_probe" in source and "/ready" in source,
        "requires_schema_lineage_live": "--require-live" in source and "disposable_stack_schema_lineage_live" in source,
        "presence_only_evidence_forbidden": "runtime_green_commands_not_executed" in source and "all_green" in source,
    }
    base_valid = all(checks.values())
    green_ok = True if not require_green else summary.get("all_green") is True
    return {
        "valid": base_valid and green_ok,
        "base_valid": base_valid,
        "require_green": require_green,
        "runtime_stack_green": summary.get("all_green") is True,
        "summary": summary,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--apply-migrations", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    result = run_runtime_stack_db_ready_green(
        ROOT,
        execute=args.execute,
        apply_migrations=args.apply_migrations,
        require_green=args.require_green,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    if args.require_green:
        return 0 if result.get("all_green") is True else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
