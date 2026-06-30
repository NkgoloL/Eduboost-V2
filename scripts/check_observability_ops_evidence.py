#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "app/core/metrics.py",
    "app/core/logging.py",
    "docs/operations/observability.md",
    "docs/incident_response.md",
    "docs/operations/support_model.md",
    "docs/operations/beta_monitoring_incident_trigger_matrix.md",
    "docs/operations/beta_participant_support_handoff_checklist.md",
    "prometheus/alerts.yml",
    "prometheus.yml",
    "grafana/dashboards.yml",
    "grafana/datasources.yml",
    "alertmanager/alertmanager.yml",
    "scripts/validate_ops_assets.py",
    "tests/test_health_metrics.py",
    "tests/unit/test_ops_assets.py",
    "tests/unit/test_beta_monitoring_incident_trigger.py",
    "tests/unit/test_beta_participant_support_handoff.py",
)


@dataclass(frozen=True)
class Result:
    target: str
    ok: bool
    detail: str


def check_all() -> list[Result]:
    return [Result(p, (ROOT / p).exists(), "present" if (ROOT / p).exists() else "missing") for p in REQUIRED]


def main() -> int:
    results = check_all()
    print("Observability/ops evidence check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
