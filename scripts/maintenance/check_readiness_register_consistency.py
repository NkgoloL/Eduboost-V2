"""Check that readiness registers and current-state summaries do not disagree."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

BOUNDARY_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "new_kg_slice_authorised",
)
DUPLICATE_KEYS = (
    "advisory_static_gate_green",
    "coverage_gate_green",
    "dependency_audit_gate_green",
    "secret_baseline_gate_green",
    "runtime_baseline_green",
    "critical_product_flows_green",
    "frontend_quality_green",
    "generated_contracts_green",
)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def _check_duplicate_fields(name: str, value: dict[str, Any], errors: list[str]) -> None:
    nested = value.get("current_truth")
    if not isinstance(nested, dict):
        errors.append(f"{name}: missing object current_truth")
        return
    for key in DUPLICATE_KEYS:
        if key in value and key in nested and value[key] != nested[key]:
            errors.append(
                f"{name}: duplicate field {key!r} differs: "
                f"top-level={value[key]!r}, current_truth={nested[key]!r}"
            )


def evaluate(root: Path) -> dict[str, Any]:
    production_path = root / "docs/roadmap/production_readiness/production_readiness_register.json"
    prd11_path = root / "docs/roadmap/production_readiness/prd11_production_release_register.json"
    remediation_path = root / "docs/roadmap/production_readiness/true_state_remediation_register.json"
    current_state_path = root / "docs/current_state.md"

    errors: list[str] = []
    production = _load(production_path)
    prd11 = _load(prd11_path)
    remediation = _load(remediation_path)
    _check_duplicate_fields("production_readiness_register", production, errors)
    _check_duplicate_fields("prd11_production_release_register", prd11, errors)

    production_next = production.get("next_authorised_item")
    prd11_next = prd11.get("next_authorised_item")
    if production_next != prd11_next:
        errors.append(
            "active readiness next item differs: "
            f"production={production_next!r}, prd11={prd11_next!r}"
        )
    for name, register, expected in (
        ("production_readiness_register", production, production_next),
        ("prd11_production_release_register", prd11, prd11_next),
    ):
        current_truth = register.get("current_truth")
        if isinstance(current_truth, dict):
            nested_next = current_truth.get("prd11_next_authorised_item")
            if nested_next is not None and nested_next != expected:
                errors.append(
                    f"{name}: current_truth.prd11_next_authorised_item differs: "
                    f"nested={nested_next!r}, top-level={expected!r}"
                )
    prd11_truth = prd11.get("current_truth")
    if isinstance(prd11_truth, dict) and prd11_truth.get("prd11_next_authorised_item") != prd11_next:
        errors.append(
            "prd11 current_truth next item differs: "
            f"top-level={prd11_next!r}, current_truth={prd11_truth.get('prd11_next_authorised_item')!r}"
        )
    if prd11.get("all_advisory_gates_green") is not False:
        errors.append("prd11 all_advisory_gates_green must remain false while any advisory gate is false")

    for key in BOUNDARY_KEYS:
        production_value = production.get(key, production.get("authority_boundaries", {}).get(key))
        prd11_value = prd11.get(key, prd11.get("authority_boundaries", {}).get(key))
        if production_value is not None and prd11_value is not None and production_value != prd11_value:
            errors.append(
                f"release boundary {key!r} differs: "
                f"production={production_value!r}, prd11={prd11_value!r}"
            )
        if production_value is not False or prd11_value is not False:
            errors.append(
                f"release boundary {key!r} is not explicitly false in both active registers: "
                f"production={production_value!r}, prd11={prd11_value!r}"
            )

    bundles = remediation.get("bundles")
    current_bundle = remediation.get("current_bundle")
    if not isinstance(bundles, list) or not current_bundle:
        errors.append("true-state remediation register lacks explicit current bundle state")
    elif not any(isinstance(bundle, dict) and bundle.get("id") == current_bundle for bundle in bundles):
        errors.append(f"true-state current_bundle {current_bundle!r} has no matching bundle entry")

    try:
        current_state = current_state_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read current-state summary: {exc}")
        current_state = ""
    active_match = re.search(r"Active implementation bundle:\s*([^\n]+)", current_state)
    if active_match and current_bundle and not active_match.group(1).startswith(str(current_bundle)):
        errors.append(
            "current-state active bundle differs from remediation register: "
            f"current_state={active_match.group(1).strip()!r}, register={current_bundle!r}"
        )

    return {
        "valid": not errors,
        "canonical_active_register": "docs/roadmap/production_readiness/prd11_production_release_register.json",
        "supporting_registers": [
            "docs/roadmap/production_readiness/production_readiness_register.json",
            "docs/roadmap/production_readiness/true_state_remediation_register.json",
        ],
        "production_next_authorised_item": production_next,
        "prd11_next_authorised_item": prd11_next,
        "remediation_current_bundle": current_bundle,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        result = evaluate(args.root.resolve())
    except ValueError as exc:
        result = {"valid": False, "errors": [str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
