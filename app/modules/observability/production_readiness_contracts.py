"""Repository-verifiable observability production-readiness contracts.

These contracts model metrics, logs, traces, SLOs, alerts, dashboards, and incident
routing without depending on a live telemetry backend. They are deterministic so the
repository can validate production-readiness evidence without Prometheus, Grafana,
OpenTelemetry Collector, Sentry, or a paging provider being configured.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import re
from typing import Mapping


class TelemetrySignal(StrEnum):
    METRIC = "metric"
    LOG = "log"
    TRACE = "trace"
    EVENT = "event"


class ServiceTier(StrEnum):
    API = "api"
    WORKER = "worker"
    FRONTEND = "frontend"
    DATABASE = "database"
    AI_PROVIDER = "ai_provider"
    BILLING_PROVIDER = "billing_provider"
    NOTIFICATION_PROVIDER = "notification_provider"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    PAGE = "page"


class IncidentRoute(StrEnum):
    ENGINEERING = "engineering"
    SECURITY = "security"
    PRIVACY = "privacy"
    RELEASE_OWNER = "release_owner"
    SUPPORT = "support"


PII_PATTERNS = (
    re.compile(r"\b[^@\s]+@[^@\s]+\.[^@\s]+\b"),
    re.compile(r"\b\d{13}\b"),
    re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"),
)


REQUIRED_CORRELATION_FIELDS = (
    "request_id",
    "trace_id",
    "span_id",
    "user_scope",
    "service",
    "environment",
)


@dataclass(frozen=True)
class ObservabilityProviderDecision:
    metrics_backend: str
    log_backend: str
    trace_backend: str
    error_backend: str
    alert_backend: str
    adr_path: str
    architecture_doc_path: str
    open_telemetry_required: bool
    pii_redaction_required: bool
    retention_policy_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("observability provider decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/observability/"):
            issues.append("observability architecture must be documented in docs/observability/")
        for name, value in {
            "metrics_backend": self.metrics_backend,
            "log_backend": self.log_backend,
            "trace_backend": self.trace_backend,
            "error_backend": self.error_backend,
            "alert_backend": self.alert_backend,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        if not self.open_telemetry_required:
            issues.append("OpenTelemetry instrumentation is required")
        if not self.pii_redaction_required:
            issues.append("PII redaction is required")
        if not self.retention_policy_required:
            issues.append("telemetry retention policy is required")
        return issues


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    description: str
    service_tier: ServiceTier
    unit: str
    labels: tuple[str, ...]
    owner: IncidentRoute
    pii_safe: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.name:
            issues.append("metric name is required")
        if not re.fullmatch(r"[a-z][a-z0-9_:]*", self.name):
            issues.append("metric name must be lowercase prometheus-style text")
        if not self.description:
            issues.append("metric description is required")
        if not self.unit:
            issues.append("metric unit is required")
        if "environment" not in self.labels:
            issues.append("metric labels must include environment")
        if "service" not in self.labels:
            issues.append("metric labels must include service")
        if not self.pii_safe:
            issues.append("metric must be PII safe")
        return issues


@dataclass(frozen=True)
class LogEventContract:
    event_name: str
    service_tier: ServiceTier
    required_fields: tuple[str, ...]
    prohibited_fields: tuple[str, ...]
    redaction_required: bool
    sample_message: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.event_name:
            issues.append("log event name is required")
        for field in REQUIRED_CORRELATION_FIELDS:
            if field not in self.required_fields:
                issues.append(f"log event missing required correlation field {field}")
        if not self.redaction_required:
            issues.append("log redaction is required")
        for prohibited in self.prohibited_fields:
            if prohibited in self.required_fields:
                issues.append(f"prohibited field {prohibited} cannot be required")
        if contains_pii(self.sample_message):
            issues.append("sample log message must not contain PII")
        return issues


@dataclass(frozen=True)
class TraceSpanContract:
    span_name: str
    service_tier: ServiceTier
    attributes: tuple[str, ...]
    propagates_request_id: bool
    propagates_trace_id: bool
    samples_errors: bool
    pii_safe: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.span_name:
            issues.append("span name is required")
        if "service" not in self.attributes:
            issues.append("span attributes must include service")
        if "environment" not in self.attributes:
            issues.append("span attributes must include environment")
        if not self.propagates_request_id:
            issues.append("request_id propagation is required")
        if not self.propagates_trace_id:
            issues.append("trace_id propagation is required")
        if not self.samples_errors:
            issues.append("error sampling is required")
        if not self.pii_safe:
            issues.append("trace attributes must be PII safe")
        return issues


@dataclass(frozen=True)
class SloDefinition:
    name: str
    service_tier: ServiceTier
    target_percentage: float
    window: str
    sli_metric: str
    burn_rate_alerts: bool
    owner: IncidentRoute

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.name:
            issues.append("SLO name is required")
        if not (0 < self.target_percentage <= 100):
            issues.append("SLO target must be between 0 and 100")
        if self.target_percentage < 90:
            issues.append("production SLO target must be at least 90 percent")
        if not self.window:
            issues.append("SLO window is required")
        if not self.sli_metric:
            issues.append("SLI metric is required")
        if not self.burn_rate_alerts:
            issues.append("burn-rate alerts are required")
        return issues


@dataclass(frozen=True)
class AlertRule:
    name: str
    severity: AlertSeverity
    service_tier: ServiceTier
    expression: str
    route: IncidentRoute
    runbook_path: str
    paging_required: bool
    deduplication_key: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.name:
            issues.append("alert name is required")
        if not self.expression:
            issues.append("alert expression is required")
        if not self.runbook_path.startswith("docs/observability/runbooks/"):
            issues.append("alert runbook must live under docs/observability/runbooks/")
        if self.severity in {AlertSeverity.CRITICAL, AlertSeverity.PAGE} and not self.paging_required:
            issues.append("critical/page alerts require paging")
        if not self.deduplication_key:
            issues.append("alert deduplication key is required")
        return issues


@dataclass(frozen=True)
class DashboardDefinition:
    dashboard_name: str
    owner: IncidentRoute
    panels: tuple[str, ...]
    links_runbooks: bool
    includes_slo_panels: bool
    includes_error_panels: bool
    includes_latency_panels: bool
    includes_traffic_panels: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.dashboard_name:
            issues.append("dashboard name is required")
        if not self.panels:
            issues.append("dashboard must include panels")
        if not self.links_runbooks:
            issues.append("dashboard must link runbooks")
        if not self.includes_slo_panels:
            issues.append("dashboard must include SLO panels")
        if not self.includes_error_panels:
            issues.append("dashboard must include error panels")
        if not self.includes_latency_panels:
            issues.append("dashboard must include latency panels")
        if not self.includes_traffic_panels:
            issues.append("dashboard must include traffic panels")
        return issues


@dataclass(frozen=True)
class TelemetryRetentionPolicy:
    metrics_days: int
    logs_days: int
    traces_days: int
    audit_logs_days: int
    pii_redaction_required: bool
    deletion_workflow_required: bool
    export_workflow_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.metrics_days <= 0:
            issues.append("metrics retention must be positive")
        if self.logs_days <= 0:
            issues.append("logs retention must be positive")
        if self.traces_days <= 0:
            issues.append("traces retention must be positive")
        if self.audit_logs_days < self.logs_days:
            issues.append("audit logs retention must be at least regular logs retention")
        if not self.pii_redaction_required:
            issues.append("PII redaction is required")
        if not self.deletion_workflow_required:
            issues.append("telemetry deletion workflow is required")
        if not self.export_workflow_required:
            issues.append("telemetry export workflow is required")
        return issues


def contains_pii(text: str) -> bool:
    """Return whether a string appears to contain common PII patterns."""

    return any(pattern.search(text or "") for pattern in PII_PATTERNS)


def redact_telemetry_text(text: str) -> str:
    """Redact obvious PII from log or telemetry metadata."""

    redacted = text or ""
    replacements = ("[redacted-email]", "[redacted-id-number]", "[redacted-phone]")
    for pattern, replacement in zip(PII_PATTERNS, replacements, strict=True):
        redacted = pattern.sub(replacement, redacted)
    return redacted


def validate_correlation_fields(payload: Mapping[str, object]) -> list[str]:
    """Validate mandatory correlation identifiers for logs/events."""

    return [field for field in REQUIRED_CORRELATION_FIELDS if not payload.get(field)]


DEFAULT_PROVIDER_DECISION = ObservabilityProviderDecision(
    metrics_backend="prometheus_or_managed_metrics",
    log_backend="structured_json_logs",
    trace_backend="opentelemetry_collector",
    error_backend="sentry_or_managed_error_tracking",
    alert_backend="alertmanager_or_managed_pager",
    adr_path="docs/adr/ADR-011-observability-stack.md",
    architecture_doc_path="docs/observability/production_observability_architecture_contract.md",
    open_telemetry_required=True,
    pii_redaction_required=True,
    retention_policy_required=True,
)

DEFAULT_METRICS = (
    MetricDefinition("eduboost_api_request_duration_seconds", "API request latency", ServiceTier.API, "seconds", ("environment", "service", "route", "method", "status"), IncidentRoute.ENGINEERING, True),
    MetricDefinition("eduboost_api_error_total", "API error count", ServiceTier.API, "count", ("environment", "service", "route", "status"), IncidentRoute.ENGINEERING, True),
    MetricDefinition("eduboost_llm_latency_seconds", "LLM provider latency", ServiceTier.AI_PROVIDER, "seconds", ("environment", "service", "provider", "model"), IncidentRoute.ENGINEERING, True),
    MetricDefinition("eduboost_billing_webhook_failure_total", "Billing webhook failures", ServiceTier.BILLING_PROVIDER, "count", ("environment", "service", "provider"), IncidentRoute.ENGINEERING, True),
    MetricDefinition("eduboost_notification_dead_letter_total", "Notification dead-letter count", ServiceTier.NOTIFICATION_PROVIDER, "count", ("environment", "service", "channel"), IncidentRoute.SUPPORT, True),
)

DEFAULT_LOG_EVENTS = (
    LogEventContract("api_request_completed", ServiceTier.API, REQUIRED_CORRELATION_FIELDS + ("route", "status_code", "duration_ms"), ("email", "phone", "raw_prompt", "password"), True, "request completed route=/api/v2/health status=200"),
    LogEventContract("llm_generation_completed", ServiceTier.AI_PROVIDER, REQUIRED_CORRELATION_FIELDS + ("provider", "model", "safety_status"), ("learner_name", "raw_prompt", "raw_output"), True, "llm generation completed safety_status=passed"),
    LogEventContract("billing_webhook_processed", ServiceTier.BILLING_PROVIDER, REQUIRED_CORRELATION_FIELDS + ("provider_event_id", "event_type"), ("card_number", "raw_provider_payload"), True, "billing webhook processed event_type=invoice.paid"),
)

DEFAULT_TRACE_SPANS = (
    TraceSpanContract("api.request", ServiceTier.API, ("service", "environment", "route", "method"), True, True, True, True),
    TraceSpanContract("database.query", ServiceTier.DATABASE, ("service", "environment", "operation", "table"), True, True, True, True),
    TraceSpanContract("llm.provider.request", ServiceTier.AI_PROVIDER, ("service", "environment", "provider", "model"), True, True, True, True),
)

DEFAULT_SLOS = (
    SloDefinition("api_availability", ServiceTier.API, 99.0, "30d", "eduboost_api_request_success_ratio", True, IncidentRoute.ENGINEERING),
    SloDefinition("api_latency", ServiceTier.API, 95.0, "30d", "eduboost_api_p95_latency_under_threshold_ratio", True, IncidentRoute.ENGINEERING),
    SloDefinition("diagnostic_generation_success", ServiceTier.AI_PROVIDER, 95.0, "30d", "eduboost_llm_generation_success_ratio", True, IncidentRoute.ENGINEERING),
)

DEFAULT_ALERTS = (
    AlertRule("api_error_rate_high", AlertSeverity.PAGE, ServiceTier.API, "rate(eduboost_api_error_total[5m]) > 0.05", IncidentRoute.ENGINEERING, "docs/observability/runbooks/api_error_rate_high.md", True, "api:error-rate"),
    AlertRule("llm_provider_failure_spike", AlertSeverity.CRITICAL, ServiceTier.AI_PROVIDER, "rate(eduboost_llm_failure_total[5m]) > 0.1", IncidentRoute.ENGINEERING, "docs/observability/runbooks/llm_provider_failure_spike.md", True, "llm:provider-failure"),
    AlertRule("notification_dead_letter_spike", AlertSeverity.WARNING, ServiceTier.NOTIFICATION_PROVIDER, "increase(eduboost_notification_dead_letter_total[15m]) > 10", IncidentRoute.SUPPORT, "docs/observability/runbooks/notification_dead_letter_spike.md", False, "notification:dead-letter"),
    AlertRule("privacy_export_failure", AlertSeverity.PAGE, ServiceTier.API, "increase(eduboost_popia_export_failure_total[10m]) > 0", IncidentRoute.PRIVACY, "docs/observability/runbooks/privacy_export_failure.md", True, "privacy:export-failure"),
)

DEFAULT_DASHBOARDS = (
    DashboardDefinition("Production API Overview", IncidentRoute.ENGINEERING, ("traffic", "latency", "errors", "saturation", "SLO burn"), True, True, True, True, True),
    DashboardDefinition("AI Provider Safety and Latency", IncidentRoute.ENGINEERING, ("LLM latency", "fallbacks", "safety rejects", "timeouts"), True, True, True, True, True),
    DashboardDefinition("Notifications and Billing Operations", IncidentRoute.SUPPORT, ("webhook failures", "dead letters", "delivery failures", "billing retries"), True, True, True, True, True),
)

DEFAULT_RETENTION_POLICY = TelemetryRetentionPolicy(
    metrics_days=180,
    logs_days=90,
    traces_days=30,
    audit_logs_days=365,
    pii_redaction_required=True,
    deletion_workflow_required=True,
    export_workflow_required=True,
)


def default_observability_readiness_report() -> dict[str, object]:
    """Return deterministic observability readiness evidence."""

    sample_payload = {
        "request_id": "req-001",
        "trace_id": "trace-001",
        "span_id": "span-001",
        "user_scope": "parent",
        "service": "api",
        "environment": "staging",
    }
    sample_text = "Contact test@example.com or +27 82 123 4567 with ID 8001015009087"

    return {
        "provider_decision_issues": DEFAULT_PROVIDER_DECISION.validate(),
        "metric_issues": [issue for metric in DEFAULT_METRICS for issue in metric.validate()],
        "log_event_issues": [issue for event in DEFAULT_LOG_EVENTS for issue in event.validate()],
        "trace_span_issues": [issue for span in DEFAULT_TRACE_SPANS for issue in span.validate()],
        "slo_issues": [issue for slo in DEFAULT_SLOS for issue in slo.validate()],
        "alert_issues": [issue for alert in DEFAULT_ALERTS for issue in alert.validate()],
        "dashboard_issues": [issue for dashboard in DEFAULT_DASHBOARDS for issue in dashboard.validate()],
        "retention_issues": DEFAULT_RETENTION_POLICY.validate(),
        "correlation_missing": validate_correlation_fields(sample_payload),
        "pii_detection_sample": contains_pii(sample_text),
        "redaction_sample": redact_telemetry_text(sample_text),
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
    }
