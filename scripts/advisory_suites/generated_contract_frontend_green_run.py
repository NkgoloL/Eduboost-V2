"""Generated-contract drift cleanup and frontend-quality green-run helpers.

PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3 is the first corrective slice that
executes the generated-contract/frontend-quality command plan as a real
blocker-clearing run. It deliberately keeps green status tied to captured
command results; policy records alone cannot make a release gate green.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/generated_contract_frontend_quality_green_run_contract.json"
PREVIOUS_CONTRACT = ROOT / "docs/roadmap/production_readiness/generated_contract_frontend_quality_execution_contract.json"
PRODUCTION_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4"
FRESHNESS_MAX_AGE_DAYS = 21
FALSE_BOUNDARIES = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "prd12_implementation_authorised",
)
REQUIRED_GATE_IDS = (
    "openapi_regenerate",
    "route_inventory_regenerate",
    "generated_contract_readonly_check",
    "frontend_typecheck",
    "frontend_lint",
    "frontend_vitest",
    "frontend_production_build",
    "frontend_release_quality",
)
REQUIRED_EVIDENCE_TYPES = (
    "independent_command_output",
    "exit_code",
    "stdout_tail",
    "stderr_tail",
    "fresh_artifact_reference",
    "blocker_record_when_not_green",
)


@dataclass(frozen=True)
class GateCommand:
    gate_id: str
    command: list[str]
    cwd: str
    output_artifact: str
    release_blocking: bool = True
    mutates_generated_contracts: bool = False


def _python() -> str:
    return sys.executable


def _pnpm() -> str:
    return os.environ.get("PNPM_BIN") or shutil.which("pnpm") or "pnpm"


def green_run_command_plan(root: Path = ROOT) -> list[dict[str, Any]]:
    py = _python()
    pnpm = _pnpm()
    commands = (
        GateCommand(
            "openapi_regenerate",
            [py, "scripts/generate_openapi.py"],
            ".",
            "openapi-regenerate.json",
            True,
            True,
        ),
        GateCommand(
            "route_inventory_regenerate",
            [py, "scripts/generate_route_inventory.py"],
            ".",
            "route-inventory-regenerate.json",
            True,
            True,
        ),
        GateCommand(
            "generated_contract_readonly_check",
            [py, "scripts/generate_openapi.py", "--check", "&&", py, "scripts/generate_route_inventory.py", "--check"],
            ".",
            "generated-contract-readonly-check.json",
            True,
            False,
        ),
        GateCommand(
            "frontend_typecheck",
            [pnpm, "run", "type-check"],
            "app/frontend",
            "frontend-typecheck.json",
        ),
        GateCommand(
            "frontend_lint",
            [pnpm, "run", "lint"],
            "app/frontend",
            "frontend-lint.json",
        ),
        GateCommand(
            "frontend_vitest",
            [pnpm, "run", "test"],
            "app/frontend",
            "frontend-vitest.json",
        ),
        GateCommand(
            "frontend_production_build",
            [pnpm, "run", "build"],
            "app/frontend",
            "frontend-build.json",
        ),
        GateCommand(
            "frontend_release_quality",
            [pnpm, "run", "quality:release"],
            "app/frontend",
            "frontend-quality-release.json",
        ),
    )
    return [asdict(command) for command in commands]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_days(value: Any, *, now: datetime | None = None) -> int | None:
    stamp = _parse_datetime(value)
    if stamp is None:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return max(0, ((now or datetime.now(timezone.utc)) - stamp).days)


def _run_single(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return {
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-8000:],
        "stderr_tail": completed.stderr[-8000:],
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def _run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    if "&&" not in command:
        return _run_single(command, cwd)
    parts: list[list[str]] = []
    current: list[str] = []
    for token in command:
        if token == "&&":
            if current:
                parts.append(current)
                current = []
            continue
        current.append(token)
    if current:
        parts.append(current)
    stdout: list[str] = []
    stderr: list[str] = []
    exit_code = 0
    for part in parts:
        result = _run_single(part, cwd)
        stdout.append(result.get("stdout_tail", ""))
        stderr.append(result.get("stderr_tail", ""))
        if result.get("exit_code") != 0:
            exit_code = int(result.get("exit_code") or 1)
            break
    return {
        "command": " && ".join(" ".join(part) for part in parts),
        "exit_code": exit_code,
        "stdout_tail": "\n".join(stdout)[-8000:],
        "stderr_tail": "\n".join(stderr)[-8000:],
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def execute_green_run(
    root: Path = ROOT,
    *,
    gates: Iterable[str] | None = None,
    output_dir: Path | None = None,
    continue_on_failure: bool = True,
) -> dict[str, Any]:
    wanted = set(gates or [])
    out = output_dir or (root / "var/prd11/runtime-restore/execution-3/generated-frontend-green-run")
    out.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for item in green_run_command_plan(root):
        if wanted and item["gate_id"] not in wanted:
            continue
        result = _run_command(list(item["command"]), root / item["cwd"])
        green = result["exit_code"] == 0
        payload = {**item, **result, "green": green}
        _write_json(out / item["output_artifact"], payload)
        results.append(payload)
        if not green and not continue_on_failure:
            break
    blockers = [item["gate_id"] for item in results if item.get("release_blocking") and not item.get("green")]
    summary = {
        "prd_id": PRD_ID,
        "executed": True,
        "results": results,
        "all_green": bool(results) and not blockers and len(results) == len(REQUIRED_GATE_IDS),
        "blockers": blockers,
        "artifact_dir": str(out.relative_to(root) if out.is_relative_to(root) else out),
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(out / "summary.json", summary)
    return summary


def _gate_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("id") in REQUIRED_GATE_IDS,
        item.get("release_blocking") is True,
        item.get("evidence_source") == "independent_command_result",
        item.get("must_execute_in_repo_environment") is True,
        item.get("presence_only_evidence_allowed") is False,
        item.get("governance_substitution_allowed") is False,
        isinstance(item.get("command"), list) and len(item.get("command")) >= 2,
        isinstance(item.get("required_evidence"), list) and set(REQUIRED_EVIDENCE_TYPES).issubset(set(item.get("required_evidence"))),
        isinstance(item.get("blocker_when_nonzero_exit"), bool) and item.get("blocker_when_nonzero_exit") is True,
    ])


def _result_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("gate_id") in REQUIRED_GATE_IDS,
        isinstance(item.get("command"), str) and item.get("command"),
        isinstance(item.get("exit_code"), int),
        isinstance(item.get("output_artifact"), str) and item.get("output_artifact"),
        isinstance(item.get("captured_at"), str) and item.get("captured_at"),
        isinstance(item.get("green"), bool),
    ])


def evaluate_governance_alignment(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load(root / PRODUCTION_REGISTER.relative_to(ROOT))
    prd11 = _load(root / PRD11_REGISTER.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    prd11_boundaries = prd11.get("authority_boundaries", {}) if isinstance(prd11.get("authority_boundaries"), dict) else {}
    release_boundaries_locked = all(boundaries.get(key) is False and prd11_boundaries.get(key) is False for key in FALSE_BOUNDARIES)
    ages = {
        "production_register_age_days": _age_days(prod.get("last_recorded_at"), now=now),
        "prd11_register_age_days": _age_days(prd11.get("last_recorded_at"), now=now),
        "contract_age_days": _age_days(_load(root / CONTRACT.relative_to(ROOT)).get("last_reviewed_at"), now=now),
    }
    fresh = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
    allowed = {PRD_ID, NEXT_AFTER_EVIDENCE, "PRD-11.0R.RUNTIME-RESTORE.EXECUTION"}
    return {
        "valid": prod_next == prd11_next and prod_next in allowed and fresh and release_boundaries_locked,
        "state_agrees": prod_next == prd11_next and prod_next in allowed,
        "production_register_next_authorised_item": prod_next,
        "prd11_register_next_authorised_item": prd11_next,
        "release_boundaries_locked": release_boundaries_locked,
        "fresh": fresh,
        **ages,
        "freshness_max_age_days": FRESHNESS_MAX_AGE_DAYS,
    }


def evaluate_green_run_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = _load(root / CONTRACT.relative_to(ROOT))
    gates = contract.get("gates", []) if isinstance(contract.get("gates"), list) else []
    gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
    missing_gates = [gate_id for gate_id in REQUIRED_GATE_IDS if gate_id not in gate_ids]
    gates_valid = all(_gate_valid(item) for item in gates if isinstance(item, dict)) and not missing_gates
    execution_results = contract.get("execution_results", []) if isinstance(contract.get("execution_results"), list) else []
    execution_results_valid = all(_result_valid(item) for item in execution_results if isinstance(item, dict))
    policy = contract.get("execution_policy", {}) if isinstance(contract.get("execution_policy"), dict) else {}
    policy_valid = all([
        policy.get("regenerate_then_readonly_check_required") is True,
        policy.get("frontend_type_lint_test_build_required") is True,
        policy.get("green_status_requires_all_release_blocking_commands_zero") is True,
        policy.get("captured_command_outputs_are_required") is True,
        policy.get("presence_only_outputs_forbidden") is True,
        policy.get("governance_records_cannot_override_failed_gate") is True,
    ])
    previous_contract = _load(root / PREVIOUS_CONTRACT.relative_to(ROOT))
    previous_valid = previous_contract.get("prd_id") == "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"
    governance = evaluate_governance_alignment(root)
    command_plan = green_run_command_plan(root)
    command_plan_valid = {item["gate_id"] for item in command_plan} == set(REQUIRED_GATE_IDS)
    all_green_from_results = bool(execution_results) and all(item.get("green") is True for item in execution_results)
    valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-execution-3/generated-frontend-green-run/v1",
        gates_valid,
        policy_valid,
        execution_results_valid,
        previous_valid,
        command_plan_valid,
        contract.get("generated_contracts_green") is False,
        contract.get("frontend_quality_green") is False,
        contract.get("next_after_evidence") == NEXT_AFTER_EVIDENCE,
        governance["valid"],
    ])
    return {
        "valid": valid,
        "prd_id": contract.get("prd_id"),
        "missing_gates": missing_gates,
        "gate_count": len(gates),
        "gates_valid": gates_valid,
        "policy_valid": policy_valid,
        "execution_results_valid": execution_results_valid,
        "previous_execution_2_contract_valid": previous_valid,
        "command_plan_valid": command_plan_valid,
        "generated_contracts_green": contract.get("generated_contracts_green") is True,
        "frontend_quality_green": contract.get("frontend_quality_green") is True,
        "all_green_from_results": all_green_from_results,
        "governance_alignment_valid": governance["valid"],
        "governance_alignment": governance,
        "next_after_evidence": contract.get("next_after_evidence"),
        "commands": command_plan,
    }
