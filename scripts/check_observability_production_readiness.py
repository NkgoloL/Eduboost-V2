#!/usr/bin/env python3
"""Validate production-readiness item 11: observability, metrics, logging, tracing, and alerting."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.observability.production_readiness_contracts import default_observability_readiness_report


REQUIRED_FILES = (
    "app/modules/observability/__init__.py",
    "app/modules/observability/production_readiness_contracts.py",
    "docs/adr/ADR-011-observability-stack.md",
    "docs/observability/production_observability_architecture_contract.md",
    "docs/observability/metrics_slo_contract.md",
    "docs/observability/logging_tracing_contract.md",
    "docs/observability/alerting_incident_routing_contract.md",
    "docs/observability/dashboard_runbook_contract.md",
    "docs/observability/telemetry_privacy_retention_contract.md",
    "docs/observability/runbooks/api_error_rate_high.md",
    "docs/observability/runbooks/llm_provider_failure_spike.md",
    "docs/observability/runbooks/notification_dead_letter_spike.md",
    "docs/observability/runbooks/privacy_export_failure.md",
    "docs/backlog/production_readiness/11_observability_metrics_logging_tracing_and_alerting.md",
    "tests/unit/test_observability_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/observability/production_readiness_contracts.py": (
        "class TelemetrySignal",
        "class ServiceTier",
        "class AlertSeverity",
        "class IncidentRoute",
        "ObservabilityProviderDecision",
        "MetricDefinition",
        "LogEventContract",
        "TraceSpanContract",
        "SloDefinition",
        "AlertRule",
        "DashboardDefinition",
        "TelemetryRetentionPolicy",
        "contains_pii",
        "redact_telemetry_text",
        "validate_correlation_fields",
        "default_observability_readiness_report",
    ),
    "docs/adr/ADR-011-observability-stack.md": (
        "Observability Stack Decision",
        "OpenTelemetry-compatible instrumentation",
        "structured JSON logging is required",
        "request ID propagation is required",
        "trace ID propagation is required",
        "PII redaction is required",
        "production SLOs are required",
        "critical alerts must page an owner",
    ),
    "docs/observability/production_observability_architecture_contract.md": (
        "Production Observability Architecture Contract",
        "OpenTelemetry-compatible instrumentation",
        "structured JSON application logs",
        "request ID propagation",
        "trace ID propagation",
        "PII redaction before telemetry retention",
        "incident routing ownership",
    ),
    "docs/observability/metrics_slo_contract.md": (
        "Metrics and SLO Contract",
        "API request duration",
        "API error count",
        "LLM provider latency",
        "billing webhook failure count",
        "notification dead-letter count",
        "API availability SLO",
        "burn-rate alerts are defined",
    ),
    "docs/observability/logging_tracing_contract.md": (
        "Logging and Tracing Contract",
        "request_id",
        "trace_id",
        "span_id",
        "raw prompt",
        "raw AI output",
        "raw provider payload",
        "API request span",
        "LLM provider request span",
        "PII-safe attributes only",
    ),
    "docs/observability/alerting_incident_routing_contract.md": (
        "Alerting and Incident Routing Contract",
        "alert expression",
        "route owner",
        "runbook path",
        "paging requirement",
        "deduplication key",
        "API error-rate spike",
        "POPIA export failure",
        "engineering",
        "privacy",
    ),
    "docs/observability/dashboard_runbook_contract.md": (
        "Dashboard and Runbook Contract",
        "Production API Overview",
        "AI Provider Safety and Latency",
        "Notifications and Billing Operations",
        "traffic",
        "latency",
        "errors",
        "SLO burn",
        "post-incident evidence",
    ),
    "docs/observability/telemetry_privacy_retention_contract.md": (
        "Telemetry Privacy and Retention Contract",
        "PII redaction before log retention",
        "PII-safe metric labels",
        "PII-safe trace attributes",
        "raw prompt exclusion",
        "raw payment provider payload exclusion",
        "telemetry deletion workflow",
        "telemetry export workflow",
        "audit logs retention period",
    ),
    "docs/backlog/production_readiness/11_observability_metrics_logging_tracing_and_alerting.md": (
        "11.6 Repository-side implementation evidence",
        "docs/observability/production_observability_architecture_contract.md",
        "scripts/check_observability_production_readiness.py",
        "make observability-production-readiness-check",
    ),
    "Makefile": (
        "observability-production-readiness-check:",
        "scripts/check_observability_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class ObservabilityReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[ObservabilityReadinessResult]:
    results: list[ObservabilityReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            ObservabilityReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                ObservabilityReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_observability_readiness_report()
        results.extend(
            [
                ObservabilityReadinessResult("observability_contracts", report["provider_decision_issues"] == [], "provider decision validates"),
                ObservabilityReadinessResult("observability_contracts", report["metric_issues"] == [], "metric definitions validate"),
                ObservabilityReadinessResult("observability_contracts", report["log_event_issues"] == [], "log event contracts validate"),
                ObservabilityReadinessResult("observability_contracts", report["trace_span_issues"] == [], "trace span contracts validate"),
                ObservabilityReadinessResult("observability_contracts", report["slo_issues"] == [], "SLO definitions validate"),
                ObservabilityReadinessResult("observability_contracts", report["alert_issues"] == [], "alert rules validate"),
                ObservabilityReadinessResult("observability_contracts", report["dashboard_issues"] == [], "dashboard definitions validate"),
                ObservabilityReadinessResult("observability_contracts", report["retention_issues"] == [], "retention policy validates"),
                ObservabilityReadinessResult("observability_contracts", report["correlation_missing"] == [], "correlation field sample validates"),
                ObservabilityReadinessResult("observability_contracts", report["pii_detection_sample"] is True, "PII detection sample passes"),
                ObservabilityReadinessResult(
                    "observability_contracts",
                    all(marker in str(report["redaction_sample"]) for marker in ("[redacted-email]", "[redacted-phone]", "[redacted-id-number]")),
                    "telemetry redaction sample passes",
                ),
            ]
        )
    except Exception as exc:  # pragma: no cover - defensive CLI output
        results.append(ObservabilityReadinessResult("observability_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Observability production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
