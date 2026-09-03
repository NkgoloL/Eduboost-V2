from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.operations_support.production_readiness_contracts import (
    DEFAULT_HANDOVER,
    DEFAULT_INCIDENT_CLASSIFICATION,
    DEFAULT_INCIDENT_RECORD,
    DEFAULT_ON_CALL_POLICIES,
    DEFAULT_OPERATIONS_DECISION,
    DEFAULT_POST_INCIDENT_REVIEW,
    DEFAULT_RUNBOOKS,
    DEFAULT_STATUS_TEMPLATES,
    DEFAULT_SUPPORT_SLAS,
    CustomerImpact,
    SupportPriority,
    classify_support_priority,
    compute_operations_evidence_checksum,
    redact_incident_note,
)
from scripts.check_incident_response_operations_support_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_incident_response_operations_support_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_incident_response_operations_support_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_incident_response_operations_support_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Incident response operations support production readiness check" in result.stdout


@pytest.mark.unit
def test_operations_support_contracts_validate() -> None:
    assert DEFAULT_OPERATIONS_DECISION.validate() == []
    assert [issue for rule in DEFAULT_INCIDENT_CLASSIFICATION for issue in rule.validate()] == []
    assert [issue for policy in DEFAULT_ON_CALL_POLICIES for issue in policy.validate()] == []
    assert [issue for runbook in DEFAULT_RUNBOOKS for issue in runbook.validate()] == []
    assert [issue for sla in DEFAULT_SUPPORT_SLAS for issue in sla.validate()] == []
    assert [issue for template in DEFAULT_STATUS_TEMPLATES for issue in template.validate()] == []
    assert DEFAULT_INCIDENT_RECORD.validate() == []
    assert DEFAULT_POST_INCIDENT_REVIEW.validate() == []
    assert DEFAULT_HANDOVER.validate() == []


@pytest.mark.unit
def test_support_priority_classification() -> None:
    assert classify_support_priority(CustomerImpact.CRITICAL, False) == SupportPriority.P0
    assert classify_support_priority(CustomerImpact.MINOR, True) == SupportPriority.P0
    assert classify_support_priority(CustomerImpact.MAJOR, False) == SupportPriority.P1
    assert classify_support_priority(CustomerImpact.MODERATE, False) == SupportPriority.P2
    assert classify_support_priority(CustomerImpact.MINOR, False) == SupportPriority.P3


@pytest.mark.unit
def test_incident_note_redaction() -> None:
    redacted = redact_incident_note("Contact user@example.com or +27 82 123 4567")
    assert "user@example.com" not in redacted
    assert "+27 82 123 4567" not in redacted
    assert "[redacted-email]" in redacted
    assert "[redacted-phone]" in redacted


@pytest.mark.unit
def test_operations_evidence_checksum_is_sha256_hex() -> None:
    checksum = compute_operations_evidence_checksum("operations-support-evidence")
    assert len(checksum) == 64
    assert checksum == compute_operations_evidence_checksum("operations-support-evidence")
    assert checksum != compute_operations_evidence_checksum("other-operations-evidence")


@pytest.mark.unit
def test_makefile_exposes_incident_response_operations_support_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "incident-response-operations-support-production-readiness-check:" in text
    assert "scripts/check_incident_response_operations_support_production_readiness.py" in text


@pytest.mark.unit
def test_operations_support_contracts_validation_error_branches() -> None:
    from datetime import datetime, timezone
    from app.modules.operations_support.production_readiness_contracts import (
        CustomerImpact,
        IncidentClassificationRule,
        IncidentRecord,
        IncidentSeverity,
        IncidentStatus,
        OnCallEscalationPolicy,
        OperationalHandoverChecklist,
        OperationalRole,
        OperationalRunbook,
        OperationsSupportDecision,
        PostIncidentReview,
        StatusCommunicationTemplate,
        SupportChannel,
        SupportPriority,
        SupportSla,
        default_operations_support_readiness_report,
    )

    # 1. OperationsSupportDecision invalid branches
    bad_dec = OperationsSupportDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        incident_response_required=False,
        on_call_required=False,
        support_sla_required=False,
        runbook_required=False,
        status_communication_required=False,
        post_incident_review_required=False,
        privacy_escalation_required=False,
    )
    dec_issues = bad_dec.validate()
    assert len(dec_issues) == 9

    # 2. IncidentClassificationRule invalid branches
    bad_rule = IncidentClassificationRule(
        severity=IncidentSeverity.SEV1,
        customer_impact=CustomerImpact.CRITICAL,
        response_time_minutes=0,
        update_interval_minutes=-1,
        requires_incident_commander=False,
        requires_status_update=False,
        requires_privacy_review=False,
        blocks_release=False,
    )
    rule_issues = bad_rule.validate()
    assert "incident response time must be positive" in rule_issues
    assert "incident update interval must be positive" in rule_issues
    assert "sev1 requires incident commander" in rule_issues
    assert "sev1 requires status update" in rule_issues
    assert "major or critical customer impact must block release" in rule_issues

    # 3. OnCallEscalationPolicy invalid branches
    bad_policy = OnCallEscalationPolicy(
        policy_id="",
        primary_role=OperationalRole.TECHNICAL_LEAD,
        secondary_role=OperationalRole.TECHNICAL_LEAD,
        escalation_minutes=0,
        coverage_hours="",
        backup_required=False,
        handoff_required=False,
        evidence_path="invalid/path.md",
    )
    policy_issues = bad_policy.validate()
    assert "policy_id is required" in policy_issues
    assert "primary and secondary roles must differ" in policy_issues
    assert "escalation minutes must be positive" in policy_issues
    assert "coverage hours are required" in policy_issues
    assert "backup on-call is required" in policy_issues
    assert "on-call handoff is required" in policy_issues
    assert "on-call evidence path must live under docs/operations_support/" in policy_issues

    # 4. OperationalRunbook invalid branches
    bad_runbook = OperationalRunbook(
        runbook_path="invalid/path.md",
        scenario="",
        owner=OperationalRole.TECHNICAL_LEAD,
        detection_steps=(),
        triage_steps=(),
        mitigation_steps=(),
        recovery_steps=(),
        verification_steps=(),
        rollback_criteria=(),
    )
    assert len(bad_runbook.validate()) == 8

    # 5. SupportSla invalid branches
    bad_sla = SupportSla(
        priority=SupportPriority.P0,
        first_response_minutes=60,
        target_resolution_hours=0,
        escalation_required=False,
        owner=OperationalRole.SUPPORT_LEAD,
        customer_visible=True,
    )
    sla_issues = bad_sla.validate()
    assert "target resolution hours must be positive" in sla_issues
    assert "p0 support requires escalation" in sla_issues
    assert "p0 first response must be <= 30 minutes" in sla_issues

    bad_p1_sla = SupportSla(
        priority=SupportPriority.P1,
        first_response_minutes=150,
        target_resolution_hours=10,
        escalation_required=True,
        owner=OperationalRole.SUPPORT_LEAD,
        customer_visible=True,
    )
    assert "p1 first response must be <= 120 minutes" in bad_p1_sla.validate()

    # 6. StatusCommunicationTemplate invalid branches
    bad_tmpl = StatusCommunicationTemplate(
        template_id="",
        severity=IncidentSeverity.SEV1,
        channels=(),
        audience="",
        update_interval_minutes=0,
        requires_privacy_review=False,
        required_fields=(),
    )
    tmpl_issues = bad_tmpl.validate()
    assert "template_id is required" in tmpl_issues
    assert "status communication channels are required" in tmpl_issues
    assert "status communication audience is required" in tmpl_issues
    assert "status update interval must be positive" in tmpl_issues
    assert "status communication missing required field incident_id" in tmpl_issues

    # 7. IncidentRecord invalid branches
    naive_dt = datetime(2026, 1, 1, 0, 0)
    bad_inc = IncidentRecord(
        incident_id="",
        severity=IncidentSeverity.SEV1,
        status=IncidentStatus.RESOLVED,
        detected_at_utc=naive_dt,
        owner=OperationalRole.INCIDENT_COMMANDER,
        customer_impact=CustomerImpact.CRITICAL,
        root_cause_summary=None,
        evidence_path="invalid/path.md",
        post_incident_review_required=False,
    )
    inc_issues = bad_inc.validate()
    assert "incident_id is required" in inc_issues
    assert "detected_at_utc must be timezone-aware" in inc_issues
    assert "resolved/reviewed incidents require root cause summary" in inc_issues
    assert "incident evidence must live under docs/operations_support/incidents/" in inc_issues
    assert "sev1/sev2 incidents require post-incident review" in inc_issues

    # 8. PostIncidentReview invalid branches
    bad_pir = PostIncidentReview(
        review_id="",
        incident_id="",
        completed=False,
        root_cause_documented=False,
        timeline_documented=False,
        corrective_actions=(),
        owner=OperationalRole.INCIDENT_COMMANDER,
        evidence_path="invalid/path.md",
    )
    assert len(bad_pir.validate()) == 7

    # 9. OperationalHandoverChecklist invalid branches
    bad_handover = OperationalHandoverChecklist(
        checklist_path="invalid/path.md",
        release_owner="",
        support_owner="",
        runbooks_reviewed=False,
        dashboards_reviewed=False,
        alert_routes_reviewed=False,
        escalation_matrix_reviewed=False,
        known_issues_reviewed=False,
        support_channels_ready=False,
    )
    assert len(bad_handover.validate()) == 9

    # 10. default_operations_support_readiness_report
    report = default_operations_support_readiness_report()
    assert report["decision_issues"] == []
    assert report["priority_sample"] == "p0"
    assert "[redacted-email]" in str(report["redaction_sample"])
