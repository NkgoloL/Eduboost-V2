"""Product critical-flow execution contract for PRD-11.0R.RUNTIME-RESTORE-4.

RESTORE-4 moves beyond taxonomy/presence checks by defining the product
critical flows whose release evidence must be produced by independent
command outputs.  The module is intentionally fail-closed: the contract can
be valid while the product gate remains red until command outputs are
captured in a later execution slice.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/product_gate_execution_contract.json"
PRODUCT_RUNTIME_CONTRACT = ROOT / "docs/roadmap/production_readiness/product_runtime_test_gate_contract.json"
TEST_TAXONOMY = ROOT / "docs/roadmap/production_readiness/test_suite_taxonomy.json"
SCRIPT_TAXONOMY = ROOT / "docs/roadmap/production_readiness/script_taxonomy.json"
COVERAGE_CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_contract.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"

PRD_ID = "PRD-11.0R.RUNTIME-RESTORE-4"
NEXT_AFTER_EVIDENCE = "PRD-11.0R.RUNTIME-RESTORE-5"
FRESHNESS_MAX_AGE_DAYS = 21
REQUIRED_FLOW_IDS = (
    "auth_authorisation",
    "popia_lifecycle",
    "billing_commercial",
    "learner_journeys",
    "diagnostics_assessments",
    "audit_trail",
)
REQUIRED_RUNTIME_DEPENDENCIES = (
    "postgres",
    "redis",
    "exact_alembic_head",
    "schema_contract",
    "ready_endpoint",
)
ALLOWED_NEXT = (PRD_ID, NEXT_AFTER_EVIDENCE, "PRD-11.0R.RUNTIME-RESTORE-6", "PRD-11.0R.RUNTIME-RESTORE.EXECUTION", "PRD-11.0-11.4")


@dataclass(frozen=True)
class CriticalFlowCommand:
    flow_id: str
    positive_command: str
    negative_command: str
    evidence_artifact: str
    requires_live_stack: bool
    release_blocking: bool = True


DEFAULT_FLOW_COMMANDS: tuple[CriticalFlowCommand, ...] = (
    CriticalFlowCommand(
        "auth_authorisation",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "product-auth-authorisation.json",
        False,
    ),
    CriticalFlowCommand(
        "popia_lifecycle",
        "PYTHONPATH=. pytest -m product tests/integration -q --no-cov --tb=short",
        "PYTHONPATH=. pytest -m product tests/integration -q --no-cov --tb=short",
        "product-popia-lifecycle.json",
        True,
    ),
    CriticalFlowCommand(
        "billing_commercial",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "product-billing-commercial.json",
        False,
    ),
    CriticalFlowCommand(
        "learner_journeys",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "product-learner-journeys.json",
        False,
    ),
    CriticalFlowCommand(
        "diagnostics_assessments",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "product-diagnostics-assessments.json",
        False,
    ),
    CriticalFlowCommand(
        "audit_trail",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "PYTHONPATH=. pytest -m product tests/unit -q --no-cov --tb=short",
        "product-audit-trail.json",
        False,
    ),
)


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


def flow_command_plan() -> list[dict[str, Any]]:
    return [asdict(command) for command in DEFAULT_FLOW_COMMANDS]


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    return _load(root / CONTRACT.relative_to(ROOT))


def _freshness(root: Path, *, now: datetime | None = None) -> dict[str, Any]:
    files = {
        "production_register_age_days": (root / PROD_REGISTER.relative_to(ROOT), "last_recorded_at"),
        "prd11_register_age_days": (root / PRD11_REGISTER.relative_to(ROOT), "last_recorded_at"),
        "test_taxonomy_age_days": (root / TEST_TAXONOMY.relative_to(ROOT), "last_reviewed_at"),
        "script_taxonomy_age_days": (root / SCRIPT_TAXONOMY.relative_to(ROOT), "last_reviewed_at"),
        "coverage_contract_age_days": (root / COVERAGE_CONTRACT.relative_to(ROOT), "last_reviewed_at"),
        "product_runtime_contract_age_days": (root / PRODUCT_RUNTIME_CONTRACT.relative_to(ROOT), "last_reviewed_at"),
        "product_gate_execution_contract_age_days": (root / CONTRACT.relative_to(ROOT), "last_reviewed_at"),
    }
    ages: dict[str, Any] = {}
    for key, (path, field) in files.items():
        ages[key] = _age_days(_load(path).get(field), now=now)
    ages["fresh"] = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
    ages["freshness_max_age_days"] = FRESHNESS_MAX_AGE_DAYS
    return ages


def evaluate_governance_alignment(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load(root / PROD_REGISTER.relative_to(ROOT))
    prd11 = _load(root / PRD11_REGISTER.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    boundaries_locked = all(boundaries.get(key) is False for key in (
        "production_release_authorised",
        "deployment_authorised",
        "release_tag_authorised",
        "public_beta_authorised",
        "public_beta_live_traffic_authorised",
        "billing_launch_authorised",
        "live_payment_processing_authorised",
    ))
    freshness = _freshness(root, now=now)
    state_agrees = prod_next == prd11_next and prod_next in ALLOWED_NEXT
    return {
        "valid": state_agrees and boundaries_locked and freshness["fresh"],
        "state_agrees": state_agrees,
        "production_register_next_authorised_item": prod_next,
        "prd11_register_next_authorised_item": prd11_next,
        "release_boundaries_locked": boundaries_locked,
        **freshness,
    }


def _flow_valid(item: dict[str, Any]) -> bool:
    return all([
        item.get("id") in REQUIRED_FLOW_IDS,
        item.get("class") == "product",
        item.get("release_blocking") is True,
        item.get("evidence_source") == "independent_command_result",
        item.get("requires_positive_path") is True,
        item.get("requires_negative_path") is True,
        item.get("requires_runtime_context") in {True, False},
        item.get("presence_only_evidence_allowed") is False,
        item.get("governance_substitution_allowed") is False,
        isinstance(item.get("positive_command"), str) and bool(item.get("positive_command")),
        isinstance(item.get("negative_command"), str) and bool(item.get("negative_command")),
        isinstance(item.get("critical_behaviours"), list) and len(item.get("critical_behaviours")) >= 2,
        isinstance(item.get("failure_modes"), list) and len(item.get("failure_modes")) >= 1,
    ])


def _execution_result_valid(item: dict[str, Any]) -> bool:
    required = (
        "flow_id",
        "positive_exit_code",
        "negative_exit_code",
        "positive_output_artifact",
        "negative_output_artifact",
        "commit_or_stack_context",
    )
    return all(key in item for key in required)


def evaluate_product_gate_execution_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_contract(root)
    flows = contract.get("critical_flows", []) if isinstance(contract.get("critical_flows"), list) else []
    flow_ids = {item.get("id") for item in flows if isinstance(item, dict)}
    missing_flows = [flow_id for flow_id in REQUIRED_FLOW_IDS if flow_id not in flow_ids]
    flows_valid = all(_flow_valid(item) for item in flows if isinstance(item, dict)) and not missing_flows
    runtime_dependencies = contract.get("runtime_dependencies", []) if isinstance(contract.get("runtime_dependencies"), list) else []
    missing_runtime_dependencies = [item for item in REQUIRED_RUNTIME_DEPENDENCIES if item not in runtime_dependencies]
    policy = contract.get("execution_policy", {}) if isinstance(contract.get("execution_policy"), dict) else {}
    policy_valid = all([
        policy.get("execute_product_gates_before_runtime_green_claim") is True,
        policy.get("capture_independent_command_outputs") is True,
        policy.get("positive_and_negative_outputs_required") is True,
        policy.get("presence_only_outputs_forbidden") is True,
        policy.get("known_failures_must_be_recorded_as_blockers") is True,
        policy.get("green_status_requires_all_flow_results_green") is True,
        policy.get("governance_records_cannot_override_failed_flow") is True,
    ])
    execution_results = contract.get("execution_results", []) if isinstance(contract.get("execution_results"), list) else []
    recorded_results_valid = all(_execution_result_valid(item) for item in execution_results if isinstance(item, dict))
    governance_alignment = evaluate_governance_alignment(root)
    valid = all([
        contract.get("prd_id") == PRD_ID,
        contract.get("schema_version") == "prd11.0r/runtime-restore-4/product-gate-execution/v1",
        flows_valid,
        not missing_runtime_dependencies,
        policy_valid,
        recorded_results_valid,
        contract.get("product_gate_green") is False,
        contract.get("next_after_evidence") == NEXT_AFTER_EVIDENCE,
        governance_alignment["valid"],
    ])
    return {
        "valid": valid,
        "prd_id": contract.get("prd_id"),
        "schema_version": contract.get("schema_version"),
        "critical_flow_ids": sorted(str(item) for item in flow_ids if item),
        "required_flow_ids": list(REQUIRED_FLOW_IDS),
        "missing_flow_ids": missing_flows,
        "flows_valid": flows_valid,
        "runtime_dependencies": runtime_dependencies,
        "missing_runtime_dependencies": missing_runtime_dependencies,
        "execution_policy_valid": policy_valid,
        "execution_results_recorded": len(execution_results),
        "execution_results_schema_valid": recorded_results_valid,
        "product_gate_green": contract.get("product_gate_green") is True,
        "governance_alignment": governance_alignment,
        "flow_command_plan": flow_command_plan(),
        "next_after_evidence": contract.get("next_after_evidence"),
    }
