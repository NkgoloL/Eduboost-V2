"""Test-suite taxonomy helpers for PRD-11.1R.

The taxonomy separates release evidence into four explicit classes:
product, runtime, governance, and advisory/static.  The helpers are intentionally
lightweight so they can run in CI without a live stack while still enforcing that
release-readiness claims cannot be proven by PRD record presence alone.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import configparser
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "docs/roadmap/production_readiness/test_suite_taxonomy.json"
PRODUCTION_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
PYTEST_INI = ROOT / "pytest.ini"
REQUIRED_CLASSES = ("product", "runtime", "governance", "advisory")
FRESHNESS_MAX_AGE_DAYS = 21
ALLOWED_PROGRESSIVE_NEXT = {
    "PRD-11.1R",
    "PRD-11.2R",
    "PRD-11.3R",
    "PRD-11.0R.RUNTIME-RESTORE",
    "PRD-11.0R.RUNTIME-RESTORE-1",
    "PRD-11.0R.RUNTIME-RESTORE-2",
    "PRD-11.0R.RUNTIME-RESTORE-3",
    "PRD-11.0R.RUNTIME-RESTORE-4",
    "PRD-11.0R.RUNTIME-RESTORE-5",
    "PRD-11.0R.RUNTIME-RESTORE-6",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-2",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-3",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-4",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-5",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-6",
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7",
}


@dataclass(frozen=True)
class SuiteCommand:
    suite_class: str
    command: str
    purpose: str
    release_blocking: bool
    requires_live_stack: bool = False


DEFAULT_SUITE_COMMANDS: tuple[SuiteCommand, ...] = (
    SuiteCommand(
        "product",
        "PYTHONPATH=. pytest -m product -q --no-cov",
        "Run product behaviour tests for services, routes, auth, POPIA, billing and learner journeys.",
        True,
    ),
    SuiteCommand(
        "runtime",
        "PYTHONPATH=. pytest -m runtime -q --no-cov",
        "Run stack/runtime tests for Postgres, Redis, migrations, schema, /ready, worker and proxy.",
        True,
        True,
    ),
    SuiteCommand(
        "governance",
        "PYTHONPATH=. pytest -m governance -q --no-cov",
        "Run PRD/evidence/register/documentation sync tests.",
        False,
    ),
    SuiteCommand(
        "advisory",
        "PYTHONPATH=. pytest -m advisory -q --no-cov",
        "Run static and advisory gates: drift, security, lint, type, coverage and dependency checks.",
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
    current = now or datetime.now(timezone.utc)
    return max(0, (current - stamp).days)


def load_pytest_markers(pytest_ini: Path = PYTEST_INI) -> set[str]:
    parser = configparser.ConfigParser(strict=False)
    parser.read(pytest_ini)
    raw = parser.get("pytest", "markers", fallback="")
    markers: set[str] = set()
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        markers.add(line.split(":", 1)[0].strip())
    return markers


def load_taxonomy(path: Path = TAXONOMY_PATH) -> dict[str, Any]:
    return _load_json(path)


def suite_commands() -> list[dict[str, Any]]:
    return [asdict(command) for command in DEFAULT_SUITE_COMMANDS]


def evaluate_governance_sync(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load_json(root / PRODUCTION_REGISTER.relative_to(ROOT))
    prd11 = _load_json(root / PRD11_REGISTER.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    prod_age = _age_days(prod.get("last_recorded_at"), now=now)
    prd11_age = _age_days(prd11.get("last_recorded_at"), now=now)
    taxonomy_age = _age_days(load_taxonomy(root / TAXONOMY_PATH.relative_to(ROOT)).get("last_reviewed_at"), now=now)
    fresh = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in (prod_age, prd11_age, taxonomy_age))
    state_agrees = prod_next == prd11_next and prod_next in ALLOWED_PROGRESSIVE_NEXT
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    release_boundaries_locked = all(
        boundaries.get(key) is False
        for key in (
            "production_release_authorised",
            "deployment_authorised",
            "release_tag_authorised",
            "public_beta_authorised",
            "public_beta_live_traffic_authorised",
            "billing_launch_authorised",
            "live_payment_processing_authorised",
        )
    )
    return {
        "valid": fresh and state_agrees and release_boundaries_locked,
        "state_agrees": state_agrees,
        "fresh": fresh,
        "freshness_max_age_days": FRESHNESS_MAX_AGE_DAYS,
        "production_register_next_authorised_item": prod_next,
        "prd11_register_next_authorised_item": prd11_next,
        "production_register_age_days": prod_age,
        "prd11_register_age_days": prd11_age,
        "taxonomy_age_days": taxonomy_age,
        "release_boundaries_locked": release_boundaries_locked,
    }


def evaluate_taxonomy(root: Path = ROOT) -> dict[str, Any]:
    taxonomy = load_taxonomy(root / TAXONOMY_PATH.relative_to(ROOT))
    markers = load_pytest_markers(root / PYTEST_INI.relative_to(ROOT))
    classes = taxonomy.get("test_classes", []) if isinstance(taxonomy.get("test_classes"), list) else []
    class_ids = {item.get("id") for item in classes if isinstance(item, dict)}
    marker_ids = {item.get("marker") for item in classes if isinstance(item, dict)}
    missing_classes = [klass for klass in REQUIRED_CLASSES if klass not in class_ids]
    missing_markers = [klass for klass in REQUIRED_CLASSES if klass not in markers or klass not in marker_ids]
    class_capabilities_valid = all(
        isinstance(item, dict)
        and item.get("id") in REQUIRED_CLASSES
        and item.get("marker") == item.get("id")
        and isinstance(item.get("required_capabilities"), list)
        and len(item.get("required_capabilities")) >= 4
        and isinstance(item.get("minimum_evidence"), list)
        and item.get("description")
        for item in classes
        if isinstance(item, dict)
    ) and len(classes) >= 4
    behavioural_rule_recorded = "presence" in str(taxonomy.get("release_gate_rule", "")).lower() or taxonomy.get("release_gate_rule")
    governance_sync = evaluate_governance_sync(root)
    valid = all([
        taxonomy.get("prd_id") == "PRD-11.1R",
        taxonomy.get("schema_version") == "prd11.1r/test-suite-taxonomy/v1",
        not missing_classes,
        not missing_markers,
        class_capabilities_valid,
        bool(behavioural_rule_recorded),
        governance_sync["valid"],
    ])
    return {
        "valid": valid,
        "prd_id": taxonomy.get("prd_id"),
        "schema_version": taxonomy.get("schema_version"),
        "required_classes": list(REQUIRED_CLASSES),
        "class_ids": sorted(str(item) for item in class_ids if item),
        "pytest_markers": sorted(markers),
        "missing_classes": missing_classes,
        "missing_markers": missing_markers,
        "class_capabilities_valid": class_capabilities_valid,
        "behavioural_rule_recorded": bool(behavioural_rule_recorded),
        "governance_sync": governance_sync,
        "suite_commands": suite_commands(),
    }


def classify_test_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if "roadmap_reconciliation" in normalized or "governance" in normalized or "release-evidence" in normalized:
        return "governance"
    if "integration" in normalized or "runtime" in normalized or "smoke" in normalized or "e2e" in normalized:
        return "runtime"
    if any(token in normalized for token in ("ruff", "mypy", "bandit", "coverage", "openapi", "route_inventory", "dependency")):
        return "advisory"
    return "product"
