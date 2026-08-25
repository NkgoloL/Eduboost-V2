"""Script taxonomy helpers for PRD-11.2R.

The taxonomy classifies scripts by release-evidence domain and by functional
role.  It is deliberately read-only and lightweight: release claims must be
backed by product/runtime/advisory command results, not by capture scripts that
write their own success state.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "docs/roadmap/production_readiness/script_taxonomy.json"
TEST_TAXONOMY_PATH = ROOT / "docs/roadmap/production_readiness/test_suite_taxonomy.json"
PRODUCTION_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
PRD11_REGISTER = ROOT / "docs/roadmap/production_readiness/prd11_production_release_register.json"
REQUIRED_CLASSES = ("product", "runtime", "governance", "advisory")
REQUIRED_ROLES = ("audit", "verify", "capture", "collect", "generate", "apply", "maintenance")
FRESHNESS_MAX_AGE_DAYS = 21
ALLOWED_PROGRESSIVE_NEXT = {
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
    "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8",
}


@dataclass(frozen=True)
class ScriptCommand:
    script_class: str
    command: str
    purpose: str
    release_blocking: bool
    requires_live_stack: bool = False


DEFAULT_SCRIPT_COMMANDS: tuple[ScriptCommand, ...] = (
    ScriptCommand(
        "product",
        "PYTHONPATH=. python3 scripts/script_suites/run_script_class.py product --dry-run --json",
        "List product-behaviour scripts for services, routes, auth, POPIA, billing and learner journeys.",
        True,
    ),
    ScriptCommand(
        "runtime",
        "PYTHONPATH=. python3 scripts/script_suites/run_script_class.py runtime --dry-run --json",
        "List runtime/stack scripts for Postgres, Redis, migrations, schema, /ready, worker and frontend proxy.",
        True,
        True,
    ),
    ScriptCommand(
        "governance",
        "PYTHONPATH=. python3 scripts/script_suites/run_script_class.py governance --dry-run --json",
        "List governance/evidence/register/documentation synchronisation scripts.",
        False,
    ),
    ScriptCommand(
        "advisory",
        "PYTHONPATH=. python3 scripts/script_suites/run_script_class.py advisory --dry-run --json",
        "List static/advisory scripts for Ruff, mypy, Bandit, coverage, dependency audit and drift checks.",
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


def script_commands() -> list[dict[str, Any]]:
    return [asdict(command) for command in DEFAULT_SCRIPT_COMMANDS]


def load_taxonomy(root: Path = ROOT) -> dict[str, Any]:
    return _load_json(root / TAXONOMY_PATH.relative_to(ROOT))


def _role_from_path(path: Path) -> str:
    name = path.name
    if name.startswith("audit_") or name.startswith("check_"):
        return "audit"
    if name.startswith("verify_"):
        return "verify"
    if name.startswith("capture_") or "capture" in name:
        return "capture"
    if name.startswith("collect_"):
        return "collect"
    if name.startswith("generate_") or name.startswith("build_"):
        return "generate"
    if name.startswith("apply_") or name.endswith(".sh"):
        return "apply"
    return "maintenance"


def classify_script_path(path: str) -> dict[str, Any]:
    normalized = path.replace("\\", "/")
    lower = normalized.lower()
    if any(token in lower for token in ("roadmap_reconciliation", "production_readiness", "release-evidence", "approval", "authority", "governance", "prd", "rr")):
        script_class = "governance"
    elif any(token in lower for token in ("ready", "readiness", "runtime", "migration", "alembic", "schema", "redis", "postgres", "worker", "docker", "deploy", "supabase", "backup", "restore")):
        script_class = "runtime"
    elif any(token in lower for token in ("ruff", "mypy", "bandit", "coverage", "openapi", "route_inventory", "dependency", "pip_audit", "audit", "lint", "security", "secrets")):
        script_class = "advisory"
    else:
        script_class = "product"
    role = _role_from_path(Path(normalized))
    return {"path": normalized, "script_class": script_class, "functional_role": role}


def inventory_scripts(root: Path = ROOT) -> list[dict[str, Any]]:
    scripts_root = root / "scripts"
    if not scripts_root.exists():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(scripts_root.rglob("*")):
        if path.is_file() and path.suffix in {".py", ".sh"}:
            items.append(classify_script_path(str(path.relative_to(root))))
    return items


def evaluate_governance_sync(root: Path = ROOT, *, now: datetime | None = None) -> dict[str, Any]:
    prod = _load_json(root / PRODUCTION_REGISTER.relative_to(ROOT))
    prd11 = _load_json(root / PRD11_REGISTER.relative_to(ROOT))
    taxonomy = load_taxonomy(root)
    test_taxonomy = _load_json(root / TEST_TAXONOMY_PATH.relative_to(ROOT))
    prod_next = prod.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    ages = {
        "production_register_age_days": _age_days(prod.get("last_recorded_at"), now=now),
        "prd11_register_age_days": _age_days(prd11.get("last_recorded_at"), now=now),
        "script_taxonomy_age_days": _age_days(taxonomy.get("last_reviewed_at"), now=now),
        "test_taxonomy_age_days": _age_days(test_taxonomy.get("last_reviewed_at"), now=now),
    }
    fresh = all(age is not None and age <= FRESHNESS_MAX_AGE_DAYS for age in ages.values())
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
        "release_boundaries_locked": release_boundaries_locked,
        **ages,
    }


def evaluate_taxonomy(root: Path = ROOT) -> dict[str, Any]:
    taxonomy = load_taxonomy(root)
    classes = taxonomy.get("script_classes", []) if isinstance(taxonomy.get("script_classes"), list) else []
    roles = taxonomy.get("functional_roles", []) if isinstance(taxonomy.get("functional_roles"), list) else []
    class_ids = {item.get("id") for item in classes if isinstance(item, dict)}
    role_ids = {item.get("id") for item in roles if isinstance(item, dict)}
    inventory = inventory_scripts(root)
    inventory_classes = {item["script_class"] for item in inventory}
    inventory_roles = {item["functional_role"] for item in inventory}
    missing_classes = [klass for klass in REQUIRED_CLASSES if klass not in class_ids]
    missing_roles = [role for role in REQUIRED_ROLES if role not in role_ids]
    missing_inventory_classes = [klass for klass in REQUIRED_CLASSES if klass not in inventory_classes]
    missing_inventory_roles = [role for role in REQUIRED_ROLES if role not in inventory_roles]
    class_capabilities_valid = all(
        isinstance(item, dict)
        and item.get("id") in REQUIRED_CLASSES
        and isinstance(item.get("required_capabilities"), list)
        and len(item.get("required_capabilities")) >= 4
        and item.get("description")
        for item in classes
        if isinstance(item, dict)
    ) and len(classes) >= 4
    role_contracts_valid = all(
        isinstance(item, dict)
        and item.get("id") in REQUIRED_ROLES
        and "may_mutate" in item
        and item.get("description")
        for item in roles
        if isinstance(item, dict)
    ) and len(roles) >= len(REQUIRED_ROLES)
    governance_sync = evaluate_governance_sync(root)
    release_gate_rule = str(taxonomy.get("release_gate_policy", "")).lower()
    no_self_proof = "cannot" in release_gate_rule and "constant" in release_gate_rule
    valid = all([
        taxonomy.get("prd_id") == "PRD-11.2R",
        taxonomy.get("schema_version") == "prd11.2r/script-taxonomy/v1",
        not missing_classes,
        not missing_roles,
        not missing_inventory_classes,
        not missing_inventory_roles,
        class_capabilities_valid,
        role_contracts_valid,
        no_self_proof,
        governance_sync["valid"],
    ])
    return {
        "valid": valid,
        "prd_id": taxonomy.get("prd_id"),
        "schema_version": taxonomy.get("schema_version"),
        "required_classes": list(REQUIRED_CLASSES),
        "required_roles": list(REQUIRED_ROLES),
        "class_ids": sorted(str(item) for item in class_ids if item),
        "role_ids": sorted(str(item) for item in role_ids if item),
        "inventory_count": len(inventory),
        "inventory_classes": sorted(inventory_classes),
        "inventory_roles": sorted(inventory_roles),
        "missing_classes": missing_classes,
        "missing_roles": missing_roles,
        "missing_inventory_classes": missing_inventory_classes,
        "missing_inventory_roles": missing_inventory_roles,
        "class_capabilities_valid": class_capabilities_valid,
        "role_contracts_valid": role_contracts_valid,
        "script_outputs_cannot_self_prove_release_readiness": no_self_proof,
        "governance_sync": governance_sync,
        "script_commands": script_commands(),
    }
