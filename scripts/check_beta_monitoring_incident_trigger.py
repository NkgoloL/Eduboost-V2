#!/usr/bin/env python3
"""Validate beta monitoring and incident trigger matrix."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "operations" / "beta_monitoring_incident_trigger_matrix.md"

REQUIRED_SNIPPETS = (
    "Beta Monitoring and Incident Trigger Matrix",
    "API availability",
    "authentication and consent denial behavior",
    "learner journey availability",
    "parent dashboard availability",
    "AI safety refusal behavior",
    "data export and deletion request paths",
    "database backup evidence freshness",
    "error envelope consistency",
    "frontend smoke journey status",
    "support intake volume",
    "API availability failure",
    "authentication or consent bypass",
    "learner data access boundary failure",
    "AI safety boundary failure",
    "database backup evidence missing",
    "frontend smoke journey failure",
    "support intake spike",
    "rollback threshold reached",
    "docs/operations/beta_rollback_runbook.md",
    "docs/operations/post_deploy_staging_smoke_checklist.md",
    "docs/security/POPIA_CONSENT_GATE_CLOSURE.md",
    "docs/ai/CLUSTER_F_CLOSURE.md",
    "docs/operations/data_resilience_evidence_index.md",
    "docs/operations/beta_release_decision_log.md",
    "does not execute rollback, create incident tickets automatically, or replace owner judgment",
    "make beta-monitoring-incident-trigger-check",
)


@dataclass(frozen=True)
class BetaMonitoringIncidentTriggerResult:
    ok: bool
    detail: str


def run_checks() -> list[BetaMonitoringIncidentTriggerResult]:
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    results = [
        BetaMonitoringIncidentTriggerResult(DOC.exists(), "matrix present" if DOC.exists() else "matrix missing")
    ]
    for snippet in REQUIRED_SNIPPETS:
        results.append(
            BetaMonitoringIncidentTriggerResult(
                snippet in text,
                f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
            )
        )
    return results


def main() -> int:
    results = run_checks()
    print("Beta monitoring and incident trigger check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
