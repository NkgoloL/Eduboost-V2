"""Product/runtime test-gate contract helpers for PRD-11.0R.RUNTIME-RESTORE-3.

The restore-3 gate turns the PRD-11.1R taxonomy into a concrete release
contract for product and runtime tests.  It deliberately does not mark the
runtime baseline green.  It verifies that product/runtime claims have explicit
positive and negative behavioural evidence requirements and that governance
records cannot be used as substitutes for those results.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/product_runtime_test_gate_contract.json"
TEST_TAXONOMY = ROOT / "docs/roadmap/production_readiness/test_suite_taxonomy.json"
SCRIPT_TAXONOMY = ROOT / "docs/roadmap/production_readiness/script_taxonomy.json"
COVERAGE_CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_contract.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
REQUIRED_PRODUCT_DOMAINS = (
    "services",
    "routes",
    "database_contracts",
    "auth_authorisation",
    "popia_lifecycle",
    "billing_commercial",
    "learner_journeys",
    "diagnostics_assessments",
)
REQUIRED_RUNTIME_DOMAINS = (
    "postgres",
    "redis",
    "migrations",
    "schema_contract",
    "ready_endpoint",
    "worker",
    "frontend_proxy",
)
ALLOWED_NEXT = ("PRD-11.0R.RUNTIME-RESTORE-3", "PRD-11.0R.RUNTIME-RESTORE-4")
FRESHNESS_MAX_AGE_DAYS = 21


@dataclass(frozen=True)
class GateCommand:
    gate_class: str
    command: str
    purpose: str
    release_blocking: bool
    requires_live_stack: bool = False


DEFAULT_GATE_COMMANDS: tuple[GateCommand, ...] = (
    GateCommand(
        "product",
        "PYTHONPATH=. python3 scripts/test_suites/run_product_runtime_gates.py product --dry-run --json",
        "List and enforce product behaviour gate commands for services, routes, DB, auth, POPIA, billing, learner journeys and diagnostics.",
        True,
    ),
    GateCommand(
        "runtime",
        "PYTHONPATH=. python3 scripts/test_suites/run_product_runtime_gates.py runtime --dry-run --json",
        "List and enforce runtime gate commands for Postgres, Redis, migrations, schema, /ready, worker and frontend proxy.",
        True,
        True,
    ),
    GateCommand(
        "combined",
        "PYTHONPATH=. python3 scripts/test_suites/verify_product_runtime_test_gates.py --json",
        "Verify that product/runtime gates require independent positive and negative behavioural evidence before release claims.",
        True,
    ),
)


def _load_json(path: Path) -> dict[str, Any]:
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


def gate_commands() -> list[dict[str, Any]]:
    return [asdict(command) for command in DEFAULT_GATE_COMMANDS]


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    return _load_json(root / CONTRACT.relative_to(ROOT))


def _domain_valid(item: dict[str, Any], *, expected_class: str) -> bool:
    evidence = item.get("required_evidence")
    negative = item.get("negative_evidence")
    command = item.get("command")
    return all([
        item.get("class") == expected_class,
        isinstance(item.get("id"), str) and bool(item.get("id")),
        isinstance(item.get("capability"), str) and bool(item.get("capability")),
        item.get("release_blocking") is True,
        item.get("evidence_source") == "independent_command_result",
        isinstance(command, str) and bool(command),
        isinstance(evidence, list) and len(evidence) >= 1,
        isinstance(negative, list) and len(negative) >= 1,
        item.get("presence_only_evidence_allowed") is False,
        item.get("governance_substitution_allowed") is False,
    ])


def evaluate_governance_alignment(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    prd11 = _load_json(root / PRD11_REGISTER.relative_to(ROOT))
    test_taxonomy = _load_json(root / TEST_TAXONOMY.relative_to(ROOT))
    script_taxonomy = _load_json(root / SCRIPT_TAXONOMY.relative_to(ROOT))
    coverage_contract = _load_json(root / COVERAGE_CONTRACT.relative_to(ROOT))
    contract = load_contract(root)
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    ages = {
        "production_register_age_days": _age_days(prod.get("last_recorded_at"), now=now),
        "prd11_register_age_days": _age_days(prd11.get("last_recorded_at"), now=now),
        "test_taxonomy_age_days": _age_days(test_taxonomy.get("last_reviewed_at"), now=now),
        "script_taxonomy_age_days": _age_days(script_taxonomy.get("last_reviewed_at"), now=now),
        "coverage_contract_age_days": _age_days(coverage_contract.get("last_reviewed_at"), now=now),
        "product_runtime_contract_age_days": _age_days(contract.get("last_reviewed_at"), now=now),
    }
    fresh = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
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
    return {
        "valid": prod_next == prd11_next and prod_next in ALLOWED_NEXT and fresh and boundaries_locked,
        "state_agrees": prod_next == prd11_next and prod_next in ALLOWED_NEXT,
        "fresh": fresh,
        "freshness_max_age_days": FRESHNESS_MAX_AGE_DAYS,
        "production_register_next_authorised_item": prod_next,
        "prd11_register_next_authorised_item": prd11_next,
        "release_boundaries_locked": boundaries_locked,
        **ages,
    }


def evaluate_product_runtime_gate_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_contract(root)
    domains = contract.get("domains", []) if isinstance(contract.get("domains"), list) else []
    product_ids = {item.get("id") for item in domains if isinstance(item, dict) and item.get("class") == "product"}
    runtime_ids = {item.get("id") for item in domains if isinstance(item, dict) and item.get("class") == "runtime"}
    missing_product = [domain for domain in REQUIRED_PRODUCT_DOMAINS if domain not in product_ids]
    missing_runtime = [domain for domain in REQUIRED_RUNTIME_DOMAINS if domain not in runtime_ids]
    product_valid = all(_domain_valid(item, expected_class="product") for item in domains if isinstance(item, dict) and item.get("class") == "product")
    runtime_valid = all(_domain_valid(item, expected_class="runtime") for item in domains if isinstance(item, dict) and item.get("class") == "runtime")
    policy = contract.get("release_gate_policy", {}) if isinstance(contract.get("release_gate_policy"), dict) else {}
    policy_valid = all([
        policy.get("independent_command_results_required") is True,
        policy.get("positive_and_negative_paths_required") is True,
        policy.get("presence_only_tests_release_blocking") is False,
        policy.get("governance_evidence_can_substitute_for_product_runtime") is False,
        policy.get("runtime_baseline_must_be_green_before_production_release_evidence") is True,
        policy.get("captured_evidence_must_store_command_outputs") is True,
    ])
    governance_alignment = evaluate_governance_alignment(root)
    valid = all([
        contract.get("prd_id") == "PRD-11.0R.RUNTIME-RESTORE-3",
        contract.get("schema_version") == "prd11.0r/runtime-restore-3/product-runtime-test-gates/v1",
        not missing_product,
        not missing_runtime,
        product_valid,
        runtime_valid,
        policy_valid,
        governance_alignment["valid"],
        contract.get("next_after_evidence") == "PRD-11.0R.RUNTIME-RESTORE-4",
    ])
    return {
        "valid": valid,
        "prd_id": contract.get("prd_id"),
        "schema_version": contract.get("schema_version"),
        "required_product_domains": list(REQUIRED_PRODUCT_DOMAINS),
        "required_runtime_domains": list(REQUIRED_RUNTIME_DOMAINS),
        "product_domain_ids": sorted(str(item) for item in product_ids if item),
        "runtime_domain_ids": sorted(str(item) for item in runtime_ids if item),
        "missing_product_domains": missing_product,
        "missing_runtime_domains": missing_runtime,
        "product_domains_valid": product_valid,
        "runtime_domains_valid": runtime_valid,
        "release_policy_valid": policy_valid,
        "governance_alignment": governance_alignment,
        "gate_commands": gate_commands(),
        "next_after_evidence": contract.get("next_after_evidence"),
    }
