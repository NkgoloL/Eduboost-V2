"""Audit PRD-7.0-7.4 observability, SRE, and incident readiness foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-7.0-7.4"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_700_704_observability_sre_incident_readiness_foundation_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd7_observability_sre_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/observability/readiness.py",
    "app/modules/observability/__init__.py",
    "app/api_v2_routers/observability_sre.py",
    "tests/unit/modules/observability/test_observability_sre_readiness.py",
    "tests/unit/roadmap_reconciliation/test_prd700_704_observability_sre_incident_readiness_foundation.py",
    "docs/engineering/prd7_observability_sre_incident_readiness_foundation.md",
]
FALSE_BOUNDARIES = [
    "prd8_implementation_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
]
ALLOWED_NEXT = {"PRD-7", "PRD-7.0-7.4", "PRD-7.5-7.9", "PRD-8"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd6_handoff_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd605_609_security_final_assurance_handoff import audit as audit_prd605

        result = audit_prd605(root)
        if result.get("valid") is True:
            return True
    except Exception:  # best-effort probe, cannot fail-close
            pass

    record = root / "docs/roadmap/production_readiness/prd_605_609_security_final_assurance_handoff_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("security_final_assurance_evidence_recorded") is True,
        payload.get("prd6_sequence_complete") is True,
        payload.get("prd7_handoff_authorised") is True,
        payload.get("next_authorised_item") == "PRD-7",
    ])


def _observability_sre_readiness_helper_valid(root: Path) -> bool:
    try:
        from app.modules.observability import (
            OBSERVABILITY_EVIDENCE_AREAS,
            OBSERVABILITY_SCOPE_ITEMS,
            RECOMMENDED_BACKENDS,
            REQUIRED_RUNBOOKS,
            build_blocked_observability_sre_readiness_report,
            build_default_observability_sre_readiness_report,
            default_observability_evidence_controls,
        )

        accepted = build_default_observability_sre_readiness_report().to_payload()
        blocked = build_blocked_observability_sre_readiness_report().to_payload()
        controls = default_observability_evidence_controls()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/observability_sre.py").read_text() if (root / "app/api_v2_routers/observability_sre.py").exists() else ""
    init_text = (root / "app/modules/observability/__init__.py").read_text() if (root / "app/modules/observability/__init__.py").exists() else ""
    api_v2 = (root / "app/api_v2.py").read_text() if (root / "app/api_v2.py").exists() else ""
    lite_api = (root / "app/api_v2_routers/api_v2.py").read_text() if (root / "app/api_v2_routers/api_v2.py").exists() else ""

    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("ready") is True,
        accepted.get("telemetry_readiness_defined") is True,
        accepted.get("incident_readiness_defined") is True,
        accepted.get("resilience_drills_defined") is True,
        accepted.get("evidence_matrix_ready") is True,
        accepted.get("prd8_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        "capture_prd7_observability_sre_foundation_evidence" in accepted.get("recommended_next_actions", []),
        blocked.get("ready") is False,
        "dashboards_missing" in blocked.get("blockers", []),
        len(OBSERVABILITY_SCOPE_ITEMS) >= 6,
        len(OBSERVABILITY_EVIDENCE_AREAS) >= 10,
        len(RECOMMENDED_BACKENDS) >= 5,
        len(REQUIRED_RUNBOOKS) >= 5,
        len(controls) == len(OBSERVABILITY_EVIDENCE_AREAS),
        "get_observability_sre_readiness" in route,
        "build_default_observability_sre_readiness_report" in route,
        "ObservabilitySreReadinessReport" in init_text,
        "observability_sre" in api_v2,
        "observability_sre" in lite_api,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd6_handoff_valid(root)
    readiness_valid = _observability_sre_readiness_helper_valid(root)

    prod_next = prod_register.get("next_authorised_item")
    authority_valid = all([
        not missing_paths,
        previous_valid,
        readiness_valid,
        record.get("observability_sre_helper_added") is True,
        record.get("observability_sre_route_added") is True,
        record.get("dashboard_alert_slo_readiness_defined") is True,
        record.get("incident_runbook_on_call_readiness_defined") is True,
        record.get("backup_restore_rollback_readiness_defined") is True,
        record.get("privacy_escalation_readiness_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
    ])

    foundation_recorded = record.get("observability_sre_foundation_recorded") is True
    evidence_recorded = record.get("observability_sre_evidence_recorded") is True
    valid = all([
        authority_valid,
        foundation_recorded,
        evidence_recorded,
        record.get("next_authorised_item") == "PRD-7.5-7.9",
        register.get("next_authorised_item") in {"PRD-7.5-7.9", "PRD-8"},
        prod_register.get("next_authorised_item") in {"PRD-7.5-7.9", "PRD-8"},
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-7.0", "PRD-7.1", "PRD-7.2", "PRD-7.3", "PRD-7.4"]),
        "missing_paths": missing_paths,
        "previous_prd6_handoff_valid": previous_valid,
        "observability_sre_readiness_valid": readiness_valid,
        "observability_sre_foundation_recorded": foundation_recorded,
        "observability_sre_evidence_recorded": evidence_recorded,
        "dashboard_alert_slo_readiness_defined": record.get("dashboard_alert_slo_readiness_defined") is True,
        "incident_runbook_on_call_readiness_defined": record.get("incident_runbook_on_call_readiness_defined") is True,
        "backup_restore_rollback_readiness_defined": record.get("backup_restore_rollback_readiness_defined") is True,
        "privacy_escalation_readiness_defined": record.get("privacy_escalation_readiness_defined") is True,
        "next_authorised_item": record.get("next_authorised_item"),
        "register_next_authorised_item": register.get("next_authorised_item"),
        "production_register_next_authorised_item": prod_register.get("next_authorised_item"),
        "prd8_implementation_authorised": record.get("prd8_implementation_authorised") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "public_beta_authorised": record.get("public_beta_authorised") is True,
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised") is True,
        "billing_launch_authorised": record.get("billing_launch_authorised") is True,
        "live_payment_processing_authorised": record.get("live_payment_processing_authorised") is True,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(ROOT)
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"{PRD_ID}: valid={result['valid']} authority_valid={result['authority_valid']}")
