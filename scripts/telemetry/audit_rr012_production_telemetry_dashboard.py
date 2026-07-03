#!/usr/bin/env python3
"""Audit RR-012 production telemetry dashboard implementation evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-012"

AUTHORITY_FILES = {
    "policy": Path("docs/telemetry/rr012_production_telemetry_dashboard_policy.md"),
    "manifest": Path("docs/telemetry/rr012_production_telemetry_manifest.json"),
    "dashboard_template": Path("docs/telemetry/rr012_production_telemetry_dashboard_attestation.template.md"),
    "inventory_template": Path("docs/telemetry/rr012_grafana_dashboard_inventory.template.json"),
    "alert_template": Path("docs/telemetry/rr012_alert_routing_validation.template.md"),
    "slo_template": Path("docs/telemetry/rr012_slo_dashboard_validation.template.md"),
    "privacy_template": Path("docs/telemetry/rr012_dashboard_privacy_boundary.template.md"),
}

EXISTING_OBSERVABILITY_CONTRACTS = {
    "observability_adr": Path("docs/adr/ADR-011-observability-stack.md"),
    "endpoint_access_adr": Path("docs/adr/ADR-027-observability-endpoint-access-control.md"),
    "production_architecture": Path("docs/observability/production_observability_architecture_contract.md"),
    "metrics_slo_contract": Path("docs/observability/metrics_slo_contract.md"),
    "dashboard_runbook_contract": Path("docs/observability/dashboard_runbook_contract.md"),
    "alerting_contract": Path("docs/observability/alerting_incident_routing_contract.md"),
    "logging_tracing_contract": Path("docs/observability/logging_tracing_contract.md"),
    "telemetry_privacy_retention_contract": Path("docs/observability/telemetry_privacy_retention_contract.md"),
    "rr008_grafana_alert_linkage": Path("docs/operations/readiness/rr008_grafana_alert_linkage.md"),
    "metrics_module": Path("app/core/metrics.py"),
    "telemetry_service": Path("app/services/telemetry.py"),
    "prometheus_alerts": Path("prometheus/alerts.yml"),
    "alertmanager_config": Path("alertmanager/alertmanager.yml"),
    "observability_workflow": Path(".github/workflows/observability_check.yml"),
}

FINAL_FILES = {
    "dashboard_attestation": Path("docs/telemetry/rr012_production_telemetry_dashboard_attestation.md"),
    "dashboard_inventory": Path("docs/telemetry/rr012_grafana_dashboard_inventory.json"),
    "alert_validation": Path("docs/telemetry/rr012_alert_routing_validation.md"),
    "slo_validation": Path("docs/telemetry/rr012_slo_dashboard_validation.md"),
    "privacy_boundary": Path("docs/telemetry/rr012_dashboard_privacy_boundary.md"),
}

REQUIRED_MARKERS = {
    "dashboard_attestation": (
        "Production telemetry dashboard implementation attested: true",
        "Grafana dashboard implementation recorded: true",
        "Production API dashboard implemented: true",
        "Learner journey dashboard implemented: true",
        "POPIA privacy operations dashboard implemented: true",
        "AI and LLM operations dashboard implemented: true",
        "Billing operations dashboard implemented: true",
        "Infrastructure readiness dashboard implemented: true",
        "Dashboard access control reviewed: true",
        "Secret values committed: false",
    ),
    "alert_validation": (
        "Alert routing validation recorded: true",
        "Prometheus rules linked: true",
        "Alertmanager route linked: true",
        "Runbook links recorded: true",
        "Pager escalation boundary recorded: true",
        "Production paging authorised: false",
    ),
    "slo_validation": (
        "SLO dashboard validation recorded: true",
        "Availability SLO panel linked: true",
        "Latency SLO panel linked: true",
        "Diagnostic success SLO panel linked: true",
        "POPIA export reliability panel linked: true",
        "Billing webhook reliability panel linked: true",
    ),
    "privacy_boundary": (
        "Dashboard privacy boundary recorded: true",
        "No learner PII exposed: true",
        "No raw prompts exposed: true",
        "No raw AI outputs exposed: true",
        "No payment card data exposed: true",
        "Role-based dashboard access required: true",
        "Production release authorised: false",
        "Deployment authorised: false",
        "Release tag authorised: false",
        "Public beta authorised: false",
        "Runtime KG implementation claimed: false",
    ),
}

AUTHORITY_MARKERS = (
    "Production telemetry dashboard authority recorded: true",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-011",
    "RR-015",
    "RR-016",
    "Billing launch authorised: false",
    "Live payment processing authorised: false",
    "Production release authorised: false",
    "Runtime KG implementation claimed: false",
)

REQUIRED_DASHBOARD_IDS = (
    "production-api-overview",
    "learner-journey-health",
    "popia-privacy-operations",
    "ai-llm-operations",
    "billing-operations",
    "infrastructure-readiness",
)


def _read(root: Path, path: Path) -> str:
    full = root / path
    return full.read_text(encoding="utf-8") if full.exists() else ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def _check_manifest(manifest: dict[str, Any], errors: list[str], checks: dict[str, bool]) -> None:
    if manifest.get("__json_error__"):
        errors.append(f"RR-012 manifest JSON invalid: {manifest['__json_error__']}")
        return
    checks["manifest_rr_id"] = manifest.get("rr_id") == RR_ID
    checks["manifest_dashboard_count"] = len(manifest.get("dashboards", [])) >= 6
    dashboard_ids = {d.get("id") for d in manifest.get("dashboards", []) if isinstance(d, dict)}
    for dashboard_id in REQUIRED_DASHBOARD_IDS:
        ok = dashboard_id in dashboard_ids
        checks[f"manifest_dashboard:{dashboard_id}"] = ok
        if not ok:
            errors.append(f"RR-012 manifest missing dashboard id: {dashboard_id}")
    boundary = manifest.get("boundary", {}) if isinstance(manifest.get("boundary"), dict) else {}
    for key in (
        "billing_launch_authorised",
        "live_payment_processing_authorised",
        "production_release_authorised",
        "deployment_authorised",
        "release_tag_authorised",
        "public_beta_authorised",
        "runtime_kg_implementation_claimed",
    ):
        checks[f"manifest_boundary_false:{key}"] = boundary.get(key) is False
        if boundary.get(key) is not False:
            errors.append(f"RR-012 manifest boundary must be false: {key}")


def _check_dashboard_inventory(root: Path, errors: list[str], final_checks: dict[str, bool]) -> None:
    inventory = _json(root, FINAL_FILES["dashboard_inventory"])
    if inventory.get("__json_error__"):
        errors.append(f"RR-012 dashboard inventory JSON invalid: {inventory['__json_error__']}")
        return
    final_checks["dashboard_inventory_rr_id"] = inventory.get("rr_id") == RR_ID
    final_checks["dashboard_inventory_recorded"] = inventory.get("grafana_dashboard_inventory_recorded") is True
    dashboards = inventory.get("dashboards", []) if isinstance(inventory.get("dashboards"), list) else []
    dashboard_ids = {d.get("id") for d in dashboards if isinstance(d, dict)}
    for dashboard_id in REQUIRED_DASHBOARD_IDS:
        ok = dashboard_id in dashboard_ids
        final_checks[f"dashboard_inventory:{dashboard_id}"] = ok
        if not ok:
            errors.append(f"RR-012 dashboard inventory missing dashboard id: {dashboard_id}")
    for key in (
        "prometheus_datasource_linked",
        "grafana_folder_recorded",
        "slo_panels_linked",
        "alert_rule_links_recorded",
        "runbook_links_recorded",
        "access_control_reviewed",
        "privacy_boundary_reviewed",
    ):
        ok = inventory.get(key) is True
        final_checks[f"dashboard_inventory:{key}"] = ok
        if not ok:
            errors.append(f"RR-012 dashboard inventory must set {key}=true")


def audit(root: Path | str = Path("."), require_final: bool = False) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    authority_checks: dict[str, bool] = {}
    for name, path in AUTHORITY_FILES.items():
        exists = (root / path).exists()
        authority_checks[f"{name}_exists"] = exists
        if not exists:
            errors.append(f"missing RR-012 authority file: {path}")

    for name, path in EXISTING_OBSERVABILITY_CONTRACTS.items():
        exists = (root / path).exists()
        authority_checks[f"existing_{name}_exists"] = exists
        if not exists:
            errors.append(f"missing existing observability contract: {path}")

    policy = _read(root, AUTHORITY_FILES["policy"])
    for marker in AUTHORITY_MARKERS:
        key = f"policy_marker:{marker}"
        authority_checks[key] = marker in policy
        if marker not in policy:
            errors.append(f"RR-012 policy missing marker: {marker}")

    manifest = _json(root, AUTHORITY_FILES["manifest"])
    _check_manifest(manifest, errors, authority_checks)

    final_checks: dict[str, bool] = {}
    if require_final:
        for name, path in FINAL_FILES.items():
            text = _read(root, path)
            exists = bool(text)
            final_checks[f"{name}_exists"] = exists
            if not exists:
                errors.append(f"missing final RR-012 evidence file: {path}")
                continue
            for marker in REQUIRED_MARKERS.get(name, ()): 
                ok = marker in text
                final_checks[f"{name}:{marker}"] = ok
                if not ok:
                    errors.append(f"final RR-012 evidence file {path} missing marker: {marker}")
        if (root / FINAL_FILES["dashboard_inventory"]).exists():
            _check_dashboard_inventory(root, errors, final_checks)
    else:
        for name, path in FINAL_FILES.items():
            if not (root / path).exists():
                warnings.append(f"missing final RR-012 evidence file before capture: {path}")

    authority_valid = not [
        e for e in errors
        if not e.startswith("missing final RR-012") and "final RR-012 evidence file" not in e and "dashboard inventory" not in e
    ]
    final_outputs_valid = require_final and not errors
    valid = authority_valid and (final_outputs_valid if require_final else True)

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "final_outputs_valid": final_outputs_valid,
        "rr_id": RR_ID,
        "authority_checks": authority_checks,
        "final_checks": final_checks,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-final", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root), require_final=args.require_final)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
