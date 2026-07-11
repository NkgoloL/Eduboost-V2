"""Generated-contract regeneration and frontend quality execution helpers.

PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2 starts executing real blocker-clearing
commands for generated API contracts and frontend quality.  The module is
careful not to turn those gates green from policy records alone: green status
requires captured independent command results.
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
CONTRACT = ROOT / "docs/roadmap/production_readiness/generated_contract_frontend_quality_execution_contract.json"
PRODUCTION_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PREVIOUS_RECORD = ROOT / "docs/roadmap/production_readiness/prd_1100r_runtime_restore_execution_1_runtime_command_frontend_generated_contracts_record.json"

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3"
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
    "generated_contract_regeneration",
    "generated_contract_drift_check",
    "frontend_typecheck",
    "frontend_lint",
    "frontend_vitest",
    "frontend_production_build",
)
REQUIRED_EVIDENCE_TYPES = (
    "independent_command_output",
    "positive_path_result",
    "negative_or_failure_path_result",
    "fresh_artifact_reference",
    "blocker_record_when_not_green",
)


@dataclass(frozen=True)
class GateCommand:
    gate_id: str
    command: list[str]
    cwd: str
    evidence_artifact: str
    release_blocking: bool = True
    negative_path_command: list[str] | None = None


def _pnpm() -> str:
    return os.environ.get("PNPM_BIN") or shutil.which("pnpm") or "pnpm"


def gate_command_plan(root: Path = ROOT) -> list[dict[str, Any]]:
    py = sys.executable
    pnpm = _pnpm()
    commands = (
        GateCommand(
            "generated_contract_regeneration",
            [py, "scripts/generate_openapi.py"],
            ".",
            "generated-openapi-regeneration.json",
            True,
            [py, "scripts/generate_openapi.py", "--check"],
        ),
        GateCommand(
            "generated_contract_drift_check",
            [py, "scripts/generate_openapi.py", "--check", "&&", py, "scripts/generate_route_inventory.py", "--check"],
            ".",
            "generated-contract-drift-check.json",
            True,
            [py, "scripts/generate_route_inventory.py", "--check"],
        ),
        GateCommand(
            "frontend_typecheck",
            [pnpm, "run", "type-check"],
            "app/frontend",
            "frontend-typecheck.json",
            True,
            [pnpm, "run", "type-check"],
        ),
        GateCommand(
            "frontend_lint",
            [pnpm, "run", "lint"],
            "app/frontend",
            "frontend-lint.json",
            True,
            [pnpm, "run", "lint:strict"],
        ),
        GateCommand(
            "frontend_vitest",
            [pnpm, "run", "test"],
            "app/frontend",
            "frontend-vitest.json",
            True,
            [pnpm, "run", "test"],
        ),
        GateCommand(
            "frontend_production_build",
            [pnpm, "run", "build"],
            "app/frontend",
            "frontend-production-build.json",
            True,
            [pnpm, "run", "quality:release"],
        ),
    )
    return [asdict(command) for command in commands]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


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


def _run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    if "&&" in command:
        parts: list[list[str]] = []
        current: list[str] = []
        for token in command:
            if token == "&&":
                parts.append(current)
                current = []
            else:
                current.append(token)
        if current:
            parts.append(current)
        combined_stdout = []
        combined_stderr = []
        exit_code = 0
        for part in parts:
            result = _run_command(part, cwd)
            combined_stdout.append(result.get("stdout_tail", ""))
            combined_stderr.append(result.get("stderr_tail", ""))
            if result.get("exit_code") != 0:
                exit_code = int(result.get("exit_code") or 1)
                break
        return {
            "command": " && ".join(" ".join(part) for part in parts),
            "exit_code": exit_code,
            "stdout_tail": "\n".join(combined_stdout)[-4000:],
            "stderr_tail": "\n".join(combined_stderr)[-4000:],
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return {
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def execute_gate_plan(root: Path = ROOT, *, gates: Iterable[str] | None = None) -> dict[str, Any]:
    wanted = set(gates or [])
    results: list[dict[str, Any]] = []
    for item in gate_command_plan(root):
        if wanted and item["gate_id"] not in wanted:
            continue
        cwd = root / item["cwd"]
        result = _run_command(list(item["command"]), cwd)
        results.append({**item, "result": result, "green": result["exit_code"] == 0})
    return {
        "executed": True,
        "results": results,
        "all_green": bool(results) and all(item["green"] for item in results),
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }


def _gate_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("id") in REQUIRED_GATE_IDS,
        item.get("release_blocking") is True,
        item.get("evidence_source") == "independent_command_result",
        item.get("requires_positive_path") is True,
        item.get("requires_negative_or_failure_path") is True,
        item.get("presence_only_evidence_allowed") is False,
        item.get("governance_substitution_allowed") is False,
        isinstance(item.get("command"), list) and len(item.get("command")) >= 2,
        isinstance(item.get("negative_or_failure_command"), list) and len(item.get("negative_or_failure_command")) >= 2,
        isinstance(item.get("required_evidence"), list) and set(REQUIRED_EVIDENCE_TYPES).issubset(set(item.get("required_evidence"))),
        isinstance(item.get("known_failure_modes"), list) and len(item.get("known_failure_modes")) >= 1,
    ])


def _execution_result_valid(item: dict[str, Any]) -> bool:
    return all(key in item for key in ("gate_id", "command", "exit_code", "output_artifact", "captured_at", "green"))


def evaluate_governance_alignment(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load(root / PRODUCTION_REGISTER.relative_to(ROOT))
    prd11 = _load(root / PRD11_REGISTER.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    release_boundaries_locked = all(boundaries.get(key) is False for key in FALSE_BOUNDARIES[:-1])
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


def evaluate_generated_frontend_quality_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = _load(root / CONTRACT.relative_to(ROOT))
    gates = contract.get("gates", []) if isinstance(contract.get("gates"), list) else []
    gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
    missing_gates = [gate_id for gate_id in REQUIRED_GATE_IDS if gate_id not in gate_ids]
    gates_valid = all(_gate_valid(item) for item in gates if isinstance(item, dict)) and not missing_gates
    execution_results = contract.get("execution_results", []) if isinstance(contract.get("execution_results"), list) else []
    execution_results_valid = all(_execution_result_valid(item) for item in execution_results if isinstance(item, dict))
    policy = contract.get("execution_policy", {}) if isinstance(contract.get("execution_policy"), dict) else {}
    policy_valid = all([
        policy.get("openapi_and_route_inventory_must_be_checked_read_only") is True,
        policy.get("regeneration_command_must_be_available") is True,
        policy.get("frontend_type_lint_vitest_build_required") is True,
        policy.get("green_status_requires_captured_command_success") is True,
        policy.get("presence_only_outputs_forbidden") is True,
        policy.get("governance_records_cannot_override_failed_gate") is True,
    ])
    package = _load(root / "app/frontend/package.json")
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}
    frontend_scripts_valid = all(name in scripts for name in ("type-check", "lint", "lint:strict", "test", "build", "quality", "quality:release"))
    governance = evaluate_governance_alignment(root)
    valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-execution-2/generated-frontend/v1",
        gates_valid,
        policy_valid,
        execution_results_valid,
        frontend_scripts_valid,
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
        "frontend_scripts_valid": frontend_scripts_valid,
        "generated_contracts_green": contract.get("generated_contracts_green") is True,
        "frontend_quality_green": contract.get("frontend_quality_green") is True,
        "governance_alignment_valid": governance["valid"],
        "governance_alignment": governance,
        "next_after_evidence": contract.get("next_after_evidence"),
        "commands": gate_command_plan(root),
    }
