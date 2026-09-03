from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.observability.production_readiness_contracts import (
    DEFAULT_ALERTS,
    DEFAULT_DASHBOARDS,
    DEFAULT_LOG_EVENTS,
    DEFAULT_METRICS,
    DEFAULT_PROVIDER_DECISION,
    DEFAULT_RETENTION_POLICY,
    DEFAULT_SLOS,
    DEFAULT_TRACE_SPANS,
    contains_pii,
    redact_telemetry_text,
    validate_correlation_fields,
)
from scripts.check_observability_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_observability_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_observability_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_observability_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Observability production readiness check" in result.stdout


@pytest.mark.unit
def test_observability_contracts_validate() -> None:
    assert DEFAULT_PROVIDER_DECISION.validate() == []
    assert [issue for metric in DEFAULT_METRICS for issue in metric.validate()] == []
    assert [issue for event in DEFAULT_LOG_EVENTS for issue in event.validate()] == []
    assert [issue for span in DEFAULT_TRACE_SPANS for issue in span.validate()] == []
    assert [issue for slo in DEFAULT_SLOS for issue in slo.validate()] == []
    assert [issue for alert in DEFAULT_ALERTS for issue in alert.validate()] == []
    assert [issue for dashboard in DEFAULT_DASHBOARDS for issue in dashboard.validate()] == []
    assert DEFAULT_RETENTION_POLICY.validate() == []


@pytest.mark.unit
def test_telemetry_pii_detection_and_redaction() -> None:
    text = "Contact test@example.com or +27 82 123 4567 with ID 8001015009087"
    redacted = redact_telemetry_text(text)

    assert contains_pii(text)
    assert "test@example.com" not in redacted
    assert "+27 82 123 4567" not in redacted
    assert "8001015009087" not in redacted
    assert "[redacted-email]" in redacted
    assert "[redacted-phone]" in redacted
    assert "[redacted-id-number]" in redacted


@pytest.mark.unit
def test_correlation_field_validation() -> None:
    assert validate_correlation_fields(
        {
            "request_id": "req-1",
            "trace_id": "trace-1",
            "span_id": "span-1",
            "user_scope": "parent",
            "service": "api",
            "environment": "test",
        }
    ) == []
    assert validate_correlation_fields({"request_id": "req-1"}) == [
        "trace_id",
        "span_id",
        "user_scope",
        "service",
        "environment",
    ]


@pytest.mark.unit
def test_makefile_exposes_observability_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "observability-production-readiness-check:" in text
    assert "scripts/check_observability_production_readiness.py" in text


@pytest.mark.unit
def test_observability_contracts_validation_error_branches() -> None:
    from app.modules.observability.production_readiness_contracts import (
        AlertRule,
        AlertSeverity,
        DashboardDefinition,
        IncidentRoute,
        LogEventContract,
        MetricDefinition,
        ObservabilityProviderDecision,
        ServiceTier,
        SloDefinition,
        TelemetryRetentionPolicy,
        TraceSpanContract,
        default_observability_readiness_report,
    )

    # 1. ObservabilityProviderDecision invalid branches
    bad_dec = ObservabilityProviderDecision(
        metrics_backend="",
        log_backend="",
        trace_backend="",
        error_backend="",
        alert_backend="",
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        open_telemetry_required=False,
        pii_redaction_required=False,
        retention_policy_required=False,
    )
    assert len(bad_dec.validate()) == 10

    # 2. MetricDefinition invalid branches
    bad_metric = MetricDefinition(
        name="INVALID-METRIC-NAME!",
        description="",
        service_tier=ServiceTier.API,
        unit="",
        labels=("route",),
        owner=IncidentRoute.ENGINEERING,
        pii_safe=False,
    )
    metric_issues = bad_metric.validate()
    assert "metric name must be lowercase prometheus-style text" in metric_issues
    assert "metric description is required" in metric_issues
    assert "metric unit is required" in metric_issues
    assert "metric labels must include environment" in metric_issues
    assert "metric labels must include service" in metric_issues
    assert "metric must be PII safe" in metric_issues

    # 3. LogEventContract invalid branches
    bad_log = LogEventContract(
        event_name="",
        service_tier=ServiceTier.API,
        required_fields=("email",),
        prohibited_fields=("email",),
        redaction_required=False,
        sample_message="user email test@example.com",
    )
    log_issues = bad_log.validate()
    assert "log event name is required" in log_issues
    assert "log redaction is required" in log_issues
    assert "prohibited field email cannot be required" in log_issues
    assert "sample log message must not contain PII" in log_issues

    # 4. TraceSpanContract invalid branches
    bad_span = TraceSpanContract(
        span_name="",
        service_tier=ServiceTier.API,
        attributes=(),
        propagates_request_id=False,
        propagates_trace_id=False,
        samples_errors=False,
        pii_safe=False,
    )
    assert len(bad_span.validate()) == 7

    # 5. SloDefinition invalid branches
    bad_slo = SloDefinition(
        name="",
        service_tier=ServiceTier.API,
        target_percentage=80.0,
        window="",
        sli_metric="",
        burn_rate_alerts=False,
        owner=IncidentRoute.ENGINEERING,
    )
    slo_issues = bad_slo.validate()
    assert "SLO name is required" in slo_issues
    assert "production SLO target must be at least 90 percent" in slo_issues
    assert "SLO window is required" in slo_issues
    assert "SLI metric is required" in slo_issues
    assert "burn-rate alerts are required" in slo_issues

    bad_slo_target = SloDefinition(
        name="n", service_tier=ServiceTier.API, target_percentage=105.0, window="w", sli_metric="m", burn_rate_alerts=True, owner=IncidentRoute.ENGINEERING
    )
    assert "SLO target must be between 0 and 100" in bad_slo_target.validate()

    # 6. AlertRule invalid branches
    bad_alert = AlertRule(
        name="",
        severity=AlertSeverity.CRITICAL,
        service_tier=ServiceTier.API,
        expression="",
        route=IncidentRoute.ENGINEERING,
        runbook_path="invalid/path.md",
        paging_required=False,
        deduplication_key="",
    )
    alert_issues = bad_alert.validate()
    assert "alert name is required" in alert_issues
    assert "alert expression is required" in alert_issues
    assert "alert runbook must live under docs/observability/runbooks/" in alert_issues
    assert "critical/page alerts require paging" in alert_issues
    assert "alert deduplication key is required" in alert_issues

    # 7. DashboardDefinition invalid branches
    bad_dash = DashboardDefinition(
        dashboard_name="",
        owner=IncidentRoute.ENGINEERING,
        panels=(),
        links_runbooks=False,
        includes_slo_panels=False,
        includes_error_panels=False,
        includes_latency_panels=False,
        includes_traffic_panels=False,
    )
    assert len(bad_dash.validate()) == 7

    # 8. TelemetryRetentionPolicy invalid branches
    bad_ret = TelemetryRetentionPolicy(
        metrics_days=0,
        logs_days=0,
        traces_days=-1,
        audit_logs_days=10,
        pii_redaction_required=False,
        deletion_workflow_required=False,
        export_workflow_required=False,
    )
    assert len(bad_ret.validate()) == 6

    # 9. default_observability_readiness_report
    report = default_observability_readiness_report()
    assert report["provider_decision_issues"] == []
    assert report["pii_detection_sample"] is True
    assert "[redacted-email]" in str(report["redaction_sample"])
