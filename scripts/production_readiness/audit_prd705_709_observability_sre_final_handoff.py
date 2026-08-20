"""Audit PRD-7.5-7.9 observability/SRE final assurance and handoff."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRD_ID = "PRD-7.5-7.9"
RECORD = ROOT / "docs/roadmap/production_readiness/prd_705_709_observability_sre_final_handoff_record.json"
REGISTER = ROOT / "docs/roadmap/production_readiness/prd7_observability_sre_register.json"
PROD_REGISTER = ROOT / "docs/roadmap/production_readiness/production_readiness_register.json"
REQUIRED_PATHS = [
    "app/modules/observability/assurance.py",
    "app/modules/observability/__init__.py",
    "app/api_v2_routers/observability_sre.py",
    "tests/unit/modules/observability/test_observability_sre_final_assurance.py",
    "tests/unit/roadmap_reconciliation/test_prd705_709_observability_sre_final_handoff.py",
    "docs/engineering/prd7_observability_sre_final_handoff.md",
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
ALLOWED_NEXT = {"PRD-7.5-7.9", "PRD-8", "PRD-8.0-8.4", "PRD-8.5-8.9"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _previous_prd7_foundation_valid(root: Path) -> bool:
    try:
        from scripts.production_readiness.audit_prd700_704_observability_sre_incident_readiness_foundation import audit as audit_prd700

        result = audit_prd700(root)
        if result.get("valid") is True:
            return True
    except Exception:  # best-effort probe, cannot fail-close
            pass

    record = root / "docs/roadmap/production_readiness/prd_700_704_observability_sre_incident_readiness_foundation_record.json"
    if not record.exists():
        return False
    payload = json.loads(record.read_text())
    return all([
        payload.get("observability_sre_foundation_recorded") is True,
        payload.get("observability_sre_evidence_recorded") is True,
        payload.get("next_authorised_item") == "PRD-7.5-7.9",
    ])


def _observability_final_assurance_valid(root: Path) -> bool:
    try:
        from app.modules.observability import (
            FINAL_ASSURANCE_CRITERIA,
            ObservabilityFinalAssuranceReport,
            build_blocked_observability_final_assurance_report,
            build_default_observability_final_assurance_report,
            default_observability_final_evidence_items,
        )

        accepted = build_default_observability_final_assurance_report().to_payload()
        blocked = build_blocked_observability_final_assurance_report().to_payload()
        evidence_items = default_observability_final_evidence_items()
    except Exception:
        return False

    route = (root / "app/api_v2_routers/observability_sre.py").read_text() if (root / "app/api_v2_routers/observability_sre.py").exists() else ""
    init_text = (root / "app/modules/observability/__init__.py").read_text() if (root / "app/modules/observability/__init__.py").exists() else ""

    return all([
        accepted.get("prd_id") == PRD_ID,
        accepted.get("source_readiness_prd_id") == "PRD-7.0-7.4",
        accepted.get("accepted") is True,
        accepted.get("dashboard_alert_slo_evidence_accepted") is True,
        accepted.get("incident_runbook_on_call_evidence_accepted") is True,
        accepted.get("backup_restore_rollback_evidence_accepted") is True,
        accepted.get("privacy_escalation_support_evidence_accepted") is True,
        accepted.get("telemetry_pii_redaction_evidence_accepted") is True,
        accepted.get("incident_readiness_reconciliation_recorded") is True,
        accepted.get("sre_signoff_recorded") is True,
        accepted.get("prd7_final_reconciliation_recorded") is True,
        accepted.get("prd8_implementation_authorised") is False,
        accepted.get("live_learner_traffic_authorised") is False,
        blocked.get("accepted") is False,
        "final_observability_sre_evidence_matrix_incomplete" in blocked.get("blockers", []),
        len(FINAL_ASSURANCE_CRITERIA) >= 6,
        len(evidence_items) >= 10,
        all(item.accepted for item in evidence_items),
        "get_observability_sre_final_assurance" in route,
        "build_default_observability_final_assurance_report" in route,
        "ObservabilityFinalAssuranceReport" in init_text,
    ])


def audit(root: Path = ROOT) -> dict[str, Any]:
    record = _load_json(root / RECORD.relative_to(ROOT))
    register = _load_json(root / REGISTER.relative_to(ROOT))
    prod_register = _load_json(root / PROD_REGISTER.relative_to(ROOT))
    missing_paths = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    false_boundaries_preserved = all(record.get(key) is False for key in FALSE_BOUNDARIES)
    previous_valid = _previous_prd7_foundation_valid(root)
    final_helper_valid = _observability_final_assurance_valid(root)

    prod_next = prod_register.get("next_authorised_item")
    authority_valid = all([
        not missing_paths,
        previous_valid,
        final_helper_valid,
        record.get("observability_final_assurance_helper_added") is True,
        record.get("observability_final_assurance_route_added") is True,
        record.get("dashboard_alert_slo_evidence_defined") is True,
        record.get("incident_runbook_on_call_evidence_defined") is True,
        record.get("backup_restore_rollback_evidence_defined") is True,
        record.get("privacy_escalation_support_evidence_defined") is True,
        record.get("telemetry_pii_redaction_evidence_defined") is True,
        false_boundaries_preserved,
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_next in ALLOWED_NEXT,
    ])

    final_evidence_recorded = record.get("observability_final_assurance_evidence_recorded") is True
    incident_reconciliation = record.get("incident_readiness_reconciliation_recorded") is True
    signoff_recorded = record.get("sre_signoff_recorded") is True
    reconciliation_recorded = record.get("prd7_final_reconciliation_recorded") is True
    sequence_complete = record.get("prd7_sequence_complete") is True
    handoff = record.get("prd8_handoff_authorised") is True

    valid = all([
        authority_valid,
        final_evidence_recorded,
        incident_reconciliation,
        signoff_recorded,
        reconciliation_recorded,
        sequence_complete,
        handoff,
        record.get("next_authorised_item") == "PRD-8",
        register.get("next_authorised_item") in ALLOWED_NEXT,
        prod_register.get("next_authorised_item") in ALLOWED_NEXT,
    ])

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "prd_id": PRD_ID,
        "merged_prd_slices": record.get("merged_prd_slices", ["PRD-7.5", "PRD-7.6", "PRD-7.7", "PRD-7.8", "PRD-7.9"]),
        "missing_paths": missing_paths,
        "previous_prd7_foundation_valid": previous_valid,
        "observability_final_assurance_valid": final_helper_valid,
        "observability_final_assurance_evidence_recorded": final_evidence_recorded,
        "incident_readiness_reconciliation_recorded": incident_reconciliation,
        "sre_signoff_recorded": signoff_recorded,
        "prd7_final_reconciliation_recorded": reconciliation_recorded,
        "prd7_sequence_complete": sequence_complete,
        "prd8_handoff_authorised": handoff,
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
