#!/usr/bin/env python3
"""Validate production-readiness item 16: incident response, operations, and support."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.operations_support.production_readiness_contracts import default_operations_support_readiness_report


REQUIRED_FILES = (
    "app/modules/operations_support/__init__.py",
    "app/modules/operations_support/production_readiness_contracts.py",
    "docs/adr/ADR-016-incident-response-operations-support.md",
    "docs/operations_support/incident_response_operations_support_architecture_contract.md",
    "docs/operations_support/incident_classification_matrix.md",
    "docs/operations_support/on_call_escalation_policy.md",
    "docs/operations_support/support_sla_policy.md",
    "docs/operations_support/status_communication_contract.md",
    "docs/operations_support/post_incident_review_contract.md",
    "docs/operations_support/production_operations_handover_checklist.md",
    "docs/operations_support/runbooks/api_outage.md",
    "docs/operations_support/runbooks/privacy_incident.md",
    "docs/operations_support/incidents/INC-001.md",
    "docs/operations_support/post_incident_reviews/PIR-001.md",
    "docs/backlog/production_readiness/16_incident_response_operations_and_support.md",
    "tests/unit/test_incident_response_operations_support_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/operations_support/production_readiness_contracts.py": (
        "class IncidentSeverity",
        "class IncidentStatus",
        "class OperationalRole",
        "class SupportPriority",
        "class SupportChannel",
        "class CustomerImpact",
        "OperationsSupportDecision",
        "IncidentClassificationRule",
        "OnCallEscalationPolicy",
        "OperationalRunbook",
        "SupportSla",
        "StatusCommunicationTemplate",
        "IncidentRecord",
        "PostIncidentReview",
        "OperationalHandoverChecklist",
        "compute_operations_evidence_checksum",
        "redact_incident_note",
        "classify_support_priority",
        "default_operations_support_readiness_report",
    ),
    "docs/adr/ADR-016-incident-response-operations-support.md": (
        "Incident Response, Operations, and Support Decision",
        "incident response is required",
        "on-call escalation is required",
        "support SLA is required",
        "privacy escalation is required",
        "sev1/sev2 incidents require incident commander",
    ),
    "docs/operations_support/incident_response_operations_support_architecture_contract.md": (
        "Incident Response Operations Support Architecture Contract",
        "incident severity model",
        "support priority model",
        "on-call escalation policy",
        "post-incident review contract",
        "privacy escalation path",
        "release-owner escalation path",
    ),
    "docs/operations_support/incident_classification_matrix.md": (
        "Incident Classification Matrix",
        "sev1 requires incident commander",
        "sev2 requires incident commander",
        "major or critical customer impact must block release",
        "privacy-related incidents require privacy review",
    ),
    "docs/operations_support/on_call_escalation_policy.md": (
        "On-Call Escalation Policy",
        "technical lead escalates to incident commander",
        "privacy lead escalates to incident commander",
        "support lead escalates to communications lead",
        "backup on-call is required",
    ),
    "docs/operations_support/support_sla_policy.md": (
        "Support SLA Policy",
        "p0 support requires escalation",
        "p1 support requires escalation",
        "p0 first response must be <= 30 minutes",
        "support cases involving privacy or security classify as p0",
    ),
    "docs/operations_support/status_communication_contract.md": (
        "Status Communication Contract",
        "sev1 status communication requires status page",
        "sev2 status communication requires status page",
        "privacy-related updates require privacy review",
        "status updates must avoid unnecessary personal information",
    ),
    "docs/operations_support/post_incident_review_contract.md": (
        "Post-Incident Review Contract",
        "sev1 incidents require post-incident review",
        "sev2 incidents require post-incident review",
        "root cause must be documented",
        "corrective actions are required",
    ),
    "docs/operations_support/production_operations_handover_checklist.md": (
        "Production Operations Handover Checklist",
        "runbooks reviewed",
        "dashboards reviewed",
        "alert routes reviewed",
        "known issues reviewed",
        "support channels ready",
        "privacy escalation reviewed",
    ),
    "docs/backlog/production_readiness/16_incident_response_operations_and_support.md": (
        "16.6 Repository-side implementation evidence",
        "docs/operations_support/incident_response_operations_support_architecture_contract.md",
        "scripts/check_incident_response_operations_support_production_readiness.py",
        "make incident-response-operations-support-production-readiness-check",
    ),
    "Makefile": (
        "incident-response-operations-support-production-readiness-check:",
        "scripts/check_incident_response_operations_support_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class OperationsSupportReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[OperationsSupportReadinessResult]:
    results: list[OperationsSupportReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            OperationsSupportReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                OperationsSupportReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_operations_support_readiness_report()
        results.extend(
            [
                OperationsSupportReadinessResult("operations_support_contracts", report["decision_issues"] == [], "operations support decision validates"),
                OperationsSupportReadinessResult("operations_support_contracts", report["classification_issues"] == [], "incident classification validates"),
                OperationsSupportReadinessResult("operations_support_contracts", report["on_call_issues"] == [], "on-call policies validate"),
                OperationsSupportReadinessResult("operations_support_contracts", report["runbook_issues"] == [], "operational runbooks validate"),
                OperationsSupportReadinessResult("operations_support_contracts", report["support_sla_issues"] == [], "support SLAs validate"),
                OperationsSupportReadinessResult("operations_support_contracts", report["status_template_issues"] == [], "status templates validate"),
                OperationsSupportReadinessResult("operations_support_contracts", report["incident_record_issues"] == [], "incident record validates"),
                OperationsSupportReadinessResult("operations_support_contracts", report["post_incident_review_issues"] == [], "post-incident review validates"),
                OperationsSupportReadinessResult("operations_support_contracts", report["handover_issues"] == [], "operational handover validates"),
                OperationsSupportReadinessResult("operations_support_contracts", report["priority_sample"] == "p0", "critical priority classification sample passes"),
                OperationsSupportReadinessResult("operations_support_contracts", report["privacy_priority_sample"] == "p0", "privacy priority classification sample passes"),
                OperationsSupportReadinessResult(
                    "operations_support_contracts",
                    "[redacted-email]" in str(report["redaction_sample"]) and "[redacted-phone]" in str(report["redaction_sample"]),
                    "incident note redaction sample passes",
                ),
                OperationsSupportReadinessResult("operations_support_contracts", len(str(report["checksum_sample"])) == 64, "operations checksum sample passes"),
            ]
        )
    except Exception as exc:  # pragma: no cover - defensive CLI output
        results.append(OperationsSupportReadinessResult("operations_support_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Incident response operations support production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
