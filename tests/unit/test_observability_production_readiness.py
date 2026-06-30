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
