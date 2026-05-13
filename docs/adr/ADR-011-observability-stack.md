# ADR-011: Observability Stack Decision

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will use OpenTelemetry-compatible instrumentation with separate contracts for metrics, structured JSON logs, distributed traces, error tracking, alerting, dashboards, and runbooks.

## Rationale

OpenTelemetry-compatible instrumentation keeps the application portable across self-hosted and managed observability backends while preserving request correlation, trace propagation, PII redaction, retention, and incident-routing controls.

## Required Controls

- OpenTelemetry instrumentation is required
- structured JSON logging is required
- request ID propagation is required
- trace ID propagation is required
- PII redaction is required
- telemetry retention policy is required
- production SLOs are required
- alert rules must link runbooks
- critical alerts must page an owner
- dashboards must link runbooks and SLO panels

## Boundary

This ADR records observability stack decision evidence. It does not configure a live telemetry provider, create dashboards, page operators, or authorize production launch.
