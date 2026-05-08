#!/usr/bin/env python3
"""Validate deployment, observability, and release-operation assets.

This is a static PR gate. It does not require Docker, Kubernetes, cloud credentials,
or a live database. It catches drift between the documented V2 runtime and the
repository's deploy/monitoring files.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - CI/dev dependency issue
    raise SystemExit("PyYAML is required. Install requirements/dev.txt") from exc

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_METRICS = {
    "eduboost_http_requests_total",
    "eduboost_http_request_duration_seconds",
    "eduboost_readiness_component_status",
    "eduboost_db_pool_size_total",
    "eduboost_db_pool_checkedout_total",
    "eduboost_db_pool_overflow_total",
    "eduboost_redis_connected_clients",
    "eduboost_arq_jobs_total",
    "eduboost_llm_requests_total",
    "eduboost_llm_tokens_total",
    "eduboost_consent_events_total",
    "eduboost_consent_gate_blocks_total",
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_yaml(path: str) -> object:
    return yaml.safe_load(read(path))


def fail(message: str) -> None:
    raise AssertionError(message)


def check_dockerfile() -> None:
    content = read("docker/Dockerfile.v2")
    if "FROM python:3.11-slim" not in content:
        fail("docker/Dockerfile.v2 must use the pinned Python slim base selected for V2")
    if "USER eduboost" not in content:
        fail("docker/Dockerfile.v2 must run production as non-root user eduboost")
    if "HEALTHCHECK" not in content or "/ready" not in content:
        fail("docker/Dockerfile.v2 must include a readiness healthcheck")
    if "uvicorn" not in content or "app.api_v2:app" not in content:
        fail("docker/Dockerfile.v2 must start the canonical app.api_v2:app runtime")
    if "LABEL org.opencontainers.image" not in content:
        fail("docker/Dockerfile.v2 must include OCI image labels")


def check_compose() -> None:
    compose = load_yaml("docker-compose.yml")
    services = compose.get("services", {}) if isinstance(compose, dict) else {}
    for name in ["api", "postgres", "redis", "prometheus", "alertmanager", "grafana", "postgres-exporter", "redis-exporter"]:
        if name not in services:
            fail(f"docker-compose.yml missing service: {name}")
    api = services["api"]
    if api.get("build", {}).get("dockerfile") != "docker/Dockerfile.v2":
        fail("api service must build docker/Dockerfile.v2")
    healthcheck = api.get("healthcheck", {})
    if "/ready" not in json.dumps(healthcheck):
        fail("api service must probe /ready")


def check_prometheus() -> None:
    prom = load_yaml("prometheus.yml")
    jobs = {job.get("job_name") for job in prom.get("scrape_configs", [])}
    expected = {"eduboost-api", "postgres", "redis"}
    missing = expected - jobs
    if missing:
        fail(f"prometheus.yml missing scrape jobs: {sorted(missing)}")
    forbidden = {"celery", "flower"} & jobs
    if forbidden:
        fail(f"prometheus.yml contains retired V1 jobs: {sorted(forbidden)}")
    if not prom.get("alerting", {}).get("alertmanagers"):
        fail("prometheus.yml must route alerts to Alertmanager")


def check_alerts_reference_real_metrics() -> None:
    metrics_source = read("app/core/metrics.py")
    alerts = read("prometheus/alerts.yml")
    metric_names = set(re.findall(r'"(eduboost_[a-zA-Z0-9_:]+)"', metrics_source))
    metric_names.update(REQUIRED_METRICS)
    referenced = set(re.findall(r"(eduboost_[a-zA-Z0-9_:]+)", alerts))
    def known_metric(name: str) -> bool:
        if name in metric_names:
            return True
        for suffix in ("_bucket", "_sum", "_count"):
            if name.endswith(suffix) and name[: -len(suffix)] in metric_names:
                return True
        return False

    unknown = sorted(
        name for name in referenced
        if not known_metric(name) and not name.startswith("eduboost_runtime_")
    )
    if unknown:
        fail(f"alerts reference metrics not defined by the app: {unknown}")
    for alert_name in ["EduBoostApiDown", "EduBoostReadinessFailure", "EduBoostHigh5xxRate", "EduBoostHighLatency", "EduBoostDatabaseUnavailable", "EduBoostRedisUnavailable", "EduBoostAuditWriteFailure", "EduBoostBackupFailure"]:
        if alert_name not in alerts:
            fail(f"prometheus/alerts.yml missing alert: {alert_name}")


def check_k8s_reference() -> None:
    docs = list(yaml.safe_load_all(read("k8s/api-deployment.yml")))
    deployment = docs[0]
    container = deployment["spec"]["template"]["spec"]["containers"][0]
    if container.get("securityContext", {}).get("runAsNonRoot") is not True:
        fail("k8s api container must set runAsNonRoot")
    if "/ready" not in json.dumps(container.get("readinessProbe", {})):
        fail("k8s api container must include /ready readinessProbe")
    if "/health" not in json.dumps(container.get("livenessProbe", {})):
        fail("k8s api container must include /health livenessProbe")
    if not container.get("resources", {}).get("requests") or not container.get("resources", {}).get("limits"):
        fail("k8s api container must set resource requests and limits")


def check_docs() -> None:
    required = [
        "docs/operations/observability.md",
        "docs/operations/deployment_runbook.md",
        "docs/operations/backup_restore_runbook.md",
        "docs/operations/staging_smoke.md",
        "docs/incident_response.md",
        "docs/disaster_recovery.md",
        "docs/environment_variables.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required ops docs: {missing}")


def main() -> int:
    checks = [
        check_dockerfile,
        check_compose,
        check_prometheus,
        check_alerts_reference_real_metrics,
        check_k8s_reference,
        check_docs,
    ]
    for check in checks:
        check()
    print("Ops assets OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Ops asset validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
