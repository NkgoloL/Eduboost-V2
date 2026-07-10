"""Documentation-defined coverage contract helpers for PRD-11.3R.

This module aligns coverage with the PRD-11.1R test taxonomy and PRD-11.2R
script taxonomy. It intentionally verifies coverage *contracts* and gate wiring;
it does not claim that the runtime baseline is green.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import configparser
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/roadmap/production_readiness/coverage_contract.json"
TEST_TAXONOMY = ROOT / "docs/roadmap/production_readiness/test_suite_taxonomy.json"
SCRIPT_TAXONOMY = ROOT / "docs/roadmap/production_readiness/script_taxonomy.json"
PRODUCTION_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
COVERAGE_DOC = ROOT / "docs/testing/coverage_quality_threshold_contract.md"
MAKEFILE = ROOT / "Makefile"
PYTEST_COVERAGE = ROOT / "pytest-coverage.ini"
COVERAGERC = ROOT / ".coveragerc"
CI_CD = ROOT / ".github/workflows/ci-cd.yml"
REQUIRED_CLASSES = ("product", "runtime", "governance", "advisory")
FRESHNESS_MAX_AGE_DAYS = 21
ALLOWED_NEXT = {"PRD-11.3R", "PRD-11.0R.RUNTIME-RESTORE", "PRD-11.0R.RUNTIME-RESTORE-1", "PRD-11.0R.RUNTIME-RESTORE-2", "PRD-11.0R.RUNTIME-RESTORE-3", "PRD-11.0R.RUNTIME-RESTORE-4"}


@dataclass(frozen=True)
class CoverageCommand:
    coverage_class: str
    command: str
    purpose: str
    release_blocking: bool
    requires_live_stack: bool = False


DEFAULT_COVERAGE_COMMANDS: tuple[CoverageCommand, ...] = (
    CoverageCommand("product", "PYTHONPATH=. pytest -m product -q --no-cov", "Product behaviour coverage for services, routes, DB, auth, POPIA, billing and learner journeys.", True),
    CoverageCommand("runtime", "PYTHONPATH=. pytest -m runtime -q --no-cov", "Runtime coverage for Postgres, Redis, migrations, schema, /ready, worker and frontend proxy.", True, True),
    CoverageCommand("governance", "PYTHONPATH=. pytest -m governance -q --no-cov", "Governance/evidence/documentation sync and freshness coverage.", False),
    CoverageCommand("advisory", "make coverage-contract-check && make openapi-check && make route-inventory-check && make test-coverage COVERAGE_THRESHOLD=70", "Advisory/static coverage for drift, dependency/security, quality and numeric coverage thresholds.", True),
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


def coverage_commands() -> list[dict[str, Any]]:
    return [asdict(command) for command in DEFAULT_COVERAGE_COMMANDS]


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    return _load_json(root / CONTRACT.relative_to(ROOT))


def _pytest_coverage_markers(path: Path) -> set[str]:
    parser = configparser.ConfigParser(strict=False)
    parser.read(path)
    raw = parser.get("pytest", "markers", fallback="")
    markers: set[str] = set()
    for line in raw.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            markers.add(line.split(":", 1)[0].strip())
    return markers


def _makefile_coverage_target(makefile_text: str) -> str:
    match = re.search(r"^test-coverage:\n(?P<body>(?:\t.*\n|\s*#.*\n|\s*\n)+)", makefile_text, re.M)
    return match.group("body") if match else ""


def evaluate_threshold_alignment(root: Path = ROOT) -> dict[str, Any]:
    contract = load_contract(root)
    thresholds = contract.get("coverage_thresholds", {}) if isinstance(contract.get("coverage_thresholds"), dict) else {}
    makefile_text = (root / MAKEFILE.relative_to(ROOT)).read_text() if (root / MAKEFILE.relative_to(ROOT)).exists() else ""
    ci_text = (root / CI_CD.relative_to(ROOT)).read_text() if (root / CI_CD.relative_to(ROOT)).exists() else ""
    pytest_cov_text = (root / PYTEST_COVERAGE.relative_to(ROOT)).read_text() if (root / PYTEST_COVERAGE.relative_to(ROOT)).exists() else ""
    coveragerc_text = (root / COVERAGERC.relative_to(ROOT)).read_text() if (root / COVERAGERC.relative_to(ROOT)).exists() else ""
    target = _makefile_coverage_target(makefile_text)
    make_threshold = None
    match = re.search(r"COVERAGE_THRESHOLD \?= (\d+)", makefile_text)
    if match:
        make_threshold = int(match.group(1))
    ci_thresholds = [int(value) for value in re.findall(r"COVERAGE_THRESHOLD:\s*\"?(\d+)\"?", ci_text)]
    markers = _pytest_coverage_markers(root / PYTEST_COVERAGE.relative_to(ROOT)) if (root / PYTEST_COVERAGE.relative_to(ROOT)).exists() else set()
    return {
        "valid": all([
            thresholds.get("minimum_line_coverage_percent", 0) >= 70,
            thresholds.get("branch_coverage_required") is True,
            "app" in thresholds.get("coverage_source_paths", []),
            make_threshold is not None and make_threshold >= 70,
            not ci_thresholds or min(ci_thresholds) >= 70,
            not any("coverage run" in line and "|| true" in line for line in target.splitlines()),
            "--cov=app" in pytest_cov_text,
            "branch = True" in coveragerc_text,
            all(marker in markers for marker in REQUIRED_CLASSES),
        ]),
        "minimum_line_coverage_percent": thresholds.get("minimum_line_coverage_percent"),
        "branch_coverage_required": thresholds.get("branch_coverage_required"),
        "coverage_source_paths": thresholds.get("coverage_source_paths"),
        "makefile_coverage_threshold": make_threshold,
        "ci_coverage_thresholds": ci_thresholds,
        "test_coverage_target_swallows_failures": any("coverage run" in line and "|| true" in line for line in target.splitlines()),
        "pytest_coverage_markers": sorted(markers),
        "pytest_coverage_has_app_source": "--cov=app" in pytest_cov_text,
        "coveragerc_branch_enabled": "branch = True" in coveragerc_text,
    }


def evaluate_governance_sync(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load_json(root / PRODUCTION_REGISTER.relative_to(ROOT))
    prd11 = _load_json(root / PRD11_REGISTER.relative_to(ROOT))
    contract = load_contract(root)
    test_taxonomy = _load_json(root / TEST_TAXONOMY.relative_to(ROOT))
    script_taxonomy = _load_json(root / SCRIPT_TAXONOMY.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    ages = {
        "production_register_age_days": _age_days(prod.get("last_recorded_at"), now=now),
        "prd11_register_age_days": _age_days(prd11.get("last_recorded_at"), now=now),
        "coverage_contract_age_days": _age_days(contract.get("last_reviewed_at"), now=now),
        "test_taxonomy_age_days": _age_days(test_taxonomy.get("last_reviewed_at"), now=now),
        "script_taxonomy_age_days": _age_days(script_taxonomy.get("last_reviewed_at"), now=now),
    }
    fresh = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
    state_agrees = prod_next == prd11_next and prod_next in ALLOWED_NEXT
    boundaries = prod.get("authority_boundaries", {}) if isinstance(prod.get("authority_boundaries"), dict) else {}
    release_boundaries_locked = all(boundaries.get(key) is False for key in (
        "production_release_authorised", "deployment_authorised", "release_tag_authorised",
        "public_beta_authorised", "public_beta_live_traffic_authorised", "billing_launch_authorised",
        "live_payment_processing_authorised",
    ))
    return {"valid": fresh and state_agrees and release_boundaries_locked, "fresh": fresh, "state_agrees": state_agrees, "freshness_max_age_days": FRESHNESS_MAX_AGE_DAYS, "production_register_next_authorised_item": prod_next, "prd11_register_next_authorised_item": prd11_next, "release_boundaries_locked": release_boundaries_locked, **ages}


def evaluate_coverage_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_contract(root)
    classes = contract.get("coverage_classes", []) if isinstance(contract.get("coverage_classes"), list) else []
    domains = contract.get("coverage_domains", []) if isinstance(contract.get("coverage_domains"), list) else []
    class_ids = {item.get("id") for item in classes if isinstance(item, dict)}
    domain_classes = {item.get("class") for item in domains if isinstance(item, dict)}
    missing_classes = [klass for klass in REQUIRED_CLASSES if klass not in class_ids]
    missing_domain_classes = [klass for klass in REQUIRED_CLASSES if klass not in domain_classes]
    domain_counts = {klass: sum(1 for item in domains if isinstance(item, dict) and item.get("class") == klass) for klass in REQUIRED_CLASSES}
    class_minimums_met = all(domain_counts[klass] >= next((int(item.get("minimum_domains", 0)) for item in classes if isinstance(item, dict) and item.get("id") == klass), 0) for klass in REQUIRED_CLASSES)
    domain_contracts_valid = bool(domains) and all(
        isinstance(item, dict)
        and item.get("class") in REQUIRED_CLASSES
        and item.get("id")
        and item.get("capability")
        and isinstance(item.get("required_evidence"), list)
        and len(item.get("required_evidence")) >= 1
        and item.get("negative_evidence_required") is True
        and "release_blocking" in item
        for item in domains
    )
    release_policy = str(contract.get("release_gate_policy", "")).lower()
    no_presence_only = "presence" in release_policy and "cannot" in release_policy
    taxonomy_classes_match = set(REQUIRED_CLASSES) == class_ids == domain_classes
    threshold_alignment = evaluate_threshold_alignment(root)
    governance_sync = evaluate_governance_sync(root)
    valid = all([
        contract.get("prd_id") == "PRD-11.3R",
        contract.get("schema_version") == "prd11.3r/documentation-defined-coverage/v1",
        not missing_classes,
        not missing_domain_classes,
        taxonomy_classes_match,
        class_minimums_met,
        domain_contracts_valid,
        no_presence_only,
        threshold_alignment["valid"],
        governance_sync["valid"],
        contract.get("next_after_evidence") == "PRD-11.0R.RUNTIME-RESTORE",
    ])
    return {
        "valid": valid,
        "prd_id": contract.get("prd_id"),
        "schema_version": contract.get("schema_version"),
        "required_classes": list(REQUIRED_CLASSES),
        "coverage_class_ids": sorted(str(item) for item in class_ids if item),
        "domain_classes": sorted(str(item) for item in domain_classes if item),
        "missing_classes": missing_classes,
        "missing_domain_classes": missing_domain_classes,
        "domain_counts": domain_counts,
        "class_minimums_met": class_minimums_met,
        "domain_contracts_valid": domain_contracts_valid,
        "taxonomy_classes_match": taxonomy_classes_match,
        "no_presence_only_release_policy": no_presence_only,
        "threshold_alignment": threshold_alignment,
        "governance_sync": governance_sync,
        "coverage_commands": coverage_commands(),
        "next_after_evidence": contract.get("next_after_evidence"),
    }
