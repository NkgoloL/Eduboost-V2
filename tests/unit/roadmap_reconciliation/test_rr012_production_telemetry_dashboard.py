from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr012_production_telemetry_dashboard.py"
    spec = importlib.util.spec_from_file_location("verify_rr012", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(root))
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)
    return module


def _copy_minimal_repo(source: Path, target: Path) -> None:
    paths = [
        "Makefile",
        ".github/workflows/rr012-production-telemetry-dashboard.yml",
        "scripts/telemetry/audit_rr012_production_telemetry_dashboard.py",
        "scripts/roadmap_reconciliation/verify_rr012_production_telemetry_dashboard.py",
        "scripts/roadmap_reconciliation/capture_rr012_production_telemetry_dashboard_evidence.py",
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_011_live_billing_provider_integration_record.json",
        "docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard.md",
        "docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard_record.json",
        "docs/adr/ADR-011-observability-stack.md",
        "docs/adr/ADR-027-observability-endpoint-access-control.md",
        "docs/observability/production_observability_architecture_contract.md",
        "docs/observability/metrics_slo_contract.md",
        "docs/observability/dashboard_runbook_contract.md",
        "docs/observability/alerting_incident_routing_contract.md",
        "docs/observability/logging_tracing_contract.md",
        "docs/observability/telemetry_privacy_retention_contract.md",
        "docs/operations/readiness/rr008_grafana_alert_linkage.md",
        "app/core/metrics.py",
        "app/services/telemetry.py",
        "prometheus/alerts.yml",
        "alertmanager/alertmanager.yml",
        ".github/workflows/observability_check.yml",
    ]
    for rel in paths:
        src = source / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copytree(source / "docs/telemetry", target / "docs/telemetry", dirs_exist_ok=True)


def _write_final_files(root: Path) -> None:
    telemetry = root / "docs/telemetry"
    telemetry.mkdir(parents=True, exist_ok=True)
    (telemetry / "rr012_production_telemetry_dashboard_attestation.md").write_text(
        """# RR-012 Production Telemetry Dashboard Attestation\n\nProduction telemetry dashboard implementation attested: true\nGrafana dashboard implementation recorded: true\nProduction API dashboard implemented: true\nLearner journey dashboard implemented: true\nPOPIA privacy operations dashboard implemented: true\nAI and LLM operations dashboard implemented: true\nBilling operations dashboard implemented: true\nInfrastructure readiness dashboard implemented: true\nDashboard access control reviewed: true\nSecret values committed: false\n""",
        encoding="utf-8",
    )
    (telemetry / "rr012_grafana_dashboard_inventory.json").write_text(
        json.dumps(
            {
                "rr_id": "RR-012",
                "grafana_dashboard_inventory_recorded": True,
                "prometheus_datasource_linked": True,
                "grafana_folder_recorded": True,
                "slo_panels_linked": True,
                "alert_rule_links_recorded": True,
                "runbook_links_recorded": True,
                "access_control_reviewed": True,
                "privacy_boundary_reviewed": True,
                "dashboards": [
                    {"id": "production-api-overview", "title": "Production API Overview"},
                    {"id": "learner-journey-health", "title": "Learner Journey Health"},
                    {"id": "popia-privacy-operations", "title": "POPIA Privacy Operations"},
                    {"id": "ai-llm-operations", "title": "AI and LLM Operations"},
                    {"id": "billing-operations", "title": "Billing Operations"},
                    {"id": "infrastructure-readiness", "title": "Infrastructure Readiness"},
                ],
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (telemetry / "rr012_alert_routing_validation.md").write_text(
        """# RR-012 Alert Routing Validation\n\nAlert routing validation recorded: true\nPrometheus rules linked: true\nAlertmanager route linked: true\nRunbook links recorded: true\nPager escalation boundary recorded: true\nProduction paging authorised: false\n""",
        encoding="utf-8",
    )
    (telemetry / "rr012_slo_dashboard_validation.md").write_text(
        """# RR-012 SLO Dashboard Validation\n\nSLO dashboard validation recorded: true\nAvailability SLO panel linked: true\nLatency SLO panel linked: true\nDiagnostic success SLO panel linked: true\nPOPIA export reliability panel linked: true\nBilling webhook reliability panel linked: true\n""",
        encoding="utf-8",
    )
    (telemetry / "rr012_dashboard_privacy_boundary.md").write_text(
        """# RR-012 Dashboard Privacy Boundary\n\nDashboard privacy boundary recorded: true\nNo learner PII exposed: true\nNo raw prompts exposed: true\nNo raw AI outputs exposed: true\nNo payment card data exposed: true\nRole-based dashboard access required: true\nProduction release authorised: false\nDeployment authorised: false\nRelease tag authorised: false\nPublic beta authorised: false\nRuntime KG implementation claimed: false\n""",
        encoding="utf-8",
    )


def test_rr012_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True, result


def test_rr012_record_becomes_valid_after_final_files_and_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    _copy_minimal_repo(source, target)
    _write_final_files(target)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_012_production_telemetry_dashboard_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "production_telemetry_dashboard_recorded": True,
            "rr011_live_billing_provider_integration_valid": True,
            "dashboard_implementation_attested": True,
            "grafana_dashboard_inventory_recorded": True,
            "production_api_dashboard_implemented": True,
            "learner_journey_dashboard_implemented": True,
            "popia_privacy_dashboard_implemented": True,
            "ai_llm_dashboard_implemented": True,
            "billing_operations_dashboard_implemented": True,
            "infrastructure_readiness_dashboard_implemented": True,
            "slo_dashboard_validation_recorded": True,
            "alert_routing_validation_recorded": True,
            "dashboard_privacy_boundary_recorded": True,
            "no_learner_pii_exposed": True,
            "secrets_not_committed_confirmed": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr013_mastery_model_research_remaining_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "production_telemetry_dashboard_audit": {"valid": True, "final_outputs_valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr012_audit_rejects_missing_final_files_when_required(tmp_path: Path) -> None:
    source = Path.cwd()
    root = tmp_path / "repo"
    _copy_minimal_repo(source, root)
    for path in (
        "rr012_production_telemetry_dashboard_attestation.md",
        "rr012_grafana_dashboard_inventory.json",
        "rr012_alert_routing_validation.md",
        "rr012_slo_dashboard_validation.md",
        "rr012_dashboard_privacy_boundary.md",
    ):
        (root / "docs/telemetry" / path).unlink()
    audit_path = root / "scripts/telemetry/audit_rr012_production_telemetry_dashboard.py"
    spec = importlib.util.spec_from_file_location("audit_rr012", audit_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit(root, require_final=True)
    assert result["authority_valid"] is True, result
    assert result["final_outputs_valid"] is False
    assert any("missing final RR-012 evidence file" in error for error in result["errors"])


def test_rr012_policy_carries_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/telemetry/rr012_production_telemetry_dashboard_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "non-required" in policy
    assert "RR-011" in policy
    assert "RR-015" in policy
    assert "RR-016" in policy
    assert "Production release authorised: false" in policy
    assert "Runtime KG implementation claimed: false" in policy


def test_rr012_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr012-production-telemetry-dashboard-audit" in text
    assert "rr012-production-telemetry-dashboard-check" in text
