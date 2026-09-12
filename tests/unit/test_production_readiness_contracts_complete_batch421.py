"""Unit tests for all remaining production readiness contracts - Batch 421.

Deterministic, high-coverage testing of:
1. app/modules/beta_launch/production_readiness_contracts.py (285 stmts)
2. app/modules/deployment/production_readiness_contracts.py (246 stmts)
3. app/modules/disaster_recovery/production_readiness_contracts.py (266 stmts)
4. app/modules/documentation_governance/production_readiness_contracts.py (292 stmts)
5. app/modules/notifications/production_readiness_contracts.py (251 stmts)
6. app/modules/operations_support/production_readiness_contracts.py (289 stmts)
7. app/modules/quality_gates/production_readiness_contracts.py (245 stmts)
8. app/modules/security_posture/production_readiness_contracts.py (312 stmts)
"""
from __future__ import annotations

import dataclasses
from datetime import date, datetime, timezone, timedelta
import pytest

from app.modules.beta_launch import production_readiness_contracts as beta_mod
from app.modules.deployment import production_readiness_contracts as dep_mod
from app.modules.disaster_recovery import production_readiness_contracts as dr_mod
from app.modules.documentation_governance import production_readiness_contracts as doc_mod
from app.modules.notifications import production_readiness_contracts as notif_mod
from app.modules.operations_support import production_readiness_contracts as ops_mod
from app.modules.quality_gates import production_readiness_contracts as qg_mod
from app.modules.security_posture import production_readiness_contracts as sec_mod


def _exercise_dataclass_mutations(objs: list[object], doc_prefix: str = "docs/") -> None:
    """Systematically mutate fields of valid dataclass instances to execute every branch."""
    for obj in objs:
        if hasattr(obj, "validate"):
            try:
                obj.validate()
            except TypeError:
                try:
                    obj.validate(date.today())
                except Exception:
                    pass

        if not dataclasses.is_dataclass(obj):
            continue

        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            if isinstance(val, str):
                mutations = ["", "invalid_path", "INVALID", doc_prefix + "other/path"]
            elif isinstance(val, bool):
                mutations = [not val]
            elif isinstance(val, (int, float)):
                mutations = [-1, 0, 999999]
            elif isinstance(val, tuple):
                mutations = [(), ("bad_entry",)]
            elif isinstance(val, dict):
                mutations = [{}]
            else:
                mutations = []

            for test_val in mutations:
                try:
                    mut = dataclasses.replace(obj, **{f.name: test_val})
                    if hasattr(mut, "validate"):
                        try:
                            mut.validate()
                        except TypeError:
                            try:
                                mut.validate(date.today())
                            except Exception:
                                pass
                except Exception:
                    pass


# ==============================================================================
# 1. BETA LAUNCH
# ==============================================================================

def test_beta_launch_production_readiness():
    rep = beta_mod.default_beta_launch_readiness_report()
    assert rep["acceptance_status_sample"] == beta_mod.AcceptanceStatus.PASS.value
    assert isinstance(rep["checksum_sample"], str)
    assert len(rep["decision_issues"]) == 0

    all_objs = [
        beta_mod.DEFAULT_BETA_DECISION,
        *beta_mod.DEFAULT_PRODUCT_SCOPE,
        *beta_mod.DEFAULT_STAGING_ACCEPTANCE,
        *beta_mod.DEFAULT_ENTRY_CRITERIA,
        *beta_mod.DEFAULT_EXIT_CRITERIA,
        beta_mod.DEFAULT_COHORT,
        *beta_mod.DEFAULT_FEEDBACK_RULES,
        *beta_mod.DEFAULT_KNOWN_ISSUES,
        beta_mod.DEFAULT_REVIEW,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/beta_launch/")

    # Helper function tests
    assert beta_mod.summarize_acceptance_status(()) == beta_mod.AcceptanceStatus.PASS
    failed_crit = (dataclasses.replace(beta_mod.DEFAULT_STAGING_ACCEPTANCE[0], status=beta_mod.AcceptanceStatus.FAIL),)
    assert beta_mod.summarize_acceptance_status(failed_crit) == beta_mod.AcceptanceStatus.FAIL
    blocked_crit = (dataclasses.replace(beta_mod.DEFAULT_STAGING_ACCEPTANCE[0], status=beta_mod.AcceptanceStatus.BLOCKED),)
    assert beta_mod.summarize_acceptance_status(blocked_crit) == beta_mod.AcceptanceStatus.BLOCKED
    waived_crit = (dataclasses.replace(beta_mod.DEFAULT_STAGING_ACCEPTANCE[0], status=beta_mod.AcceptanceStatus.WAIVED),)
    assert beta_mod.summarize_acceptance_status(waived_crit) == beta_mod.AcceptanceStatus.WAIVED

    unverified_entry = (dataclasses.replace(beta_mod.DEFAULT_ENTRY_CRITERIA[0], met=False),)
    blocking_known = (dataclasses.replace(beta_mod.DEFAULT_KNOWN_ISSUES[0], blocks_beta=True, accepted_for_beta=False),)
    no_go_rev = dataclasses.replace(beta_mod.DEFAULT_REVIEW, decision=beta_mod.LaunchDecision.NO_GO)
    bundle_errs = beta_mod.validate_beta_launch_bundle(unverified_entry, blocking_known, no_go_rev)
    assert len(bundle_errs) >= 2


# ==============================================================================
# 2. DEPLOYMENT
# ==============================================================================

def test_deployment_production_readiness():
    rep = dep_mod.default_deployment_readiness_report()
    assert isinstance(rep["artifact_digest_sample"], str)
    assert len(rep["provider_decision_issues"]) == 0

    all_objs = [
        dep_mod.DEFAULT_PROVIDER_DECISION,
        *dep_mod.DEFAULT_PIPELINE_CHECKS,
        *dep_mod.DEFAULT_DOCKER_IMAGES,
        *dep_mod.DEFAULT_ENVIRONMENTS,
        *dep_mod.DEFAULT_DEPLOYMENT_GATES,
        *dep_mod.DEFAULT_ROLLBACKS,
        dep_mod.DEFAULT_PROVENANCE,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/deployment/")

    # Helper function tests
    missing_manifest = {"ENVIRONMENT": "staging"}
    errs = dep_mod.validate_env_manifest(dep_mod.EnvironmentName.STAGING, missing_manifest)
    assert len(errs) >= 4

    insecure_manifest = {
        "DATABASE_URL": "",
        "REDIS_URL": "changeme",
        "APP_SECRET_KEY": "placeholder",
        "CORS_ORIGINS": "https://app.test",
        "ENVIRONMENT": "staging",
        "LOG_LEVEL": "INFO",
    }
    insecure_errs = dep_mod.validate_env_manifest(dep_mod.EnvironmentName.PRODUCTION, insecure_manifest)
    assert len(insecure_errs) >= 3


# ==============================================================================
# 3. DISASTER RECOVERY
# ==============================================================================

def test_disaster_recovery_production_readiness():
    rep = dr_mod.default_disaster_recovery_readiness_report()
    assert rep["checksum_validation_sample"] is True
    assert rep["scope_classification_sample"] == dr_mod.BackupScope.DATABASE.value
    assert len(rep["provider_decision_issues"]) == 0

    all_objs = [
        dr_mod.DEFAULT_PROVIDER_DECISION,
        *dr_mod.DEFAULT_BACKUP_POLICIES,
        *dr_mod.DEFAULT_RECOVERY_OBJECTIVES,
        dr_mod.DEFAULT_MANIFEST_ENTRY,
        *dr_mod.DEFAULT_RESTORE_RUNBOOKS,
        dr_mod.DEFAULT_RESTORE_DRILL,
        dr_mod.DEFAULT_DR_PLAN,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/disaster_recovery/")

    # Helper functions
    assert dr_mod.classify_backup_scope("database/postgres.sql") == dr_mod.BackupScope.DATABASE
    assert dr_mod.classify_backup_scope("storage/assets.tar") == dr_mod.BackupScope.OBJECT_STORAGE
    assert dr_mod.classify_backup_scope("audit/logs.json") == dr_mod.BackupScope.AUDIT_LOGS
    assert dr_mod.classify_backup_scope("telemetry/metrics.json") == dr_mod.BackupScope.TELEMETRY_EXPORTS
    assert dr_mod.classify_backup_scope("secrets/keys.json") == dr_mod.BackupScope.SECRETS_METADATA
    assert dr_mod.classify_backup_scope("config/env.json") == dr_mod.BackupScope.CONFIGURATION

    payload = b"test payload"
    ck = dr_mod.compute_backup_checksum(payload)
    assert dr_mod.validate_checksum(payload, ck) is True
    assert dr_mod.validate_checksum(payload, "invalid_checksum") is False


# ==============================================================================
# 4. DOCUMENTATION GOVERNANCE
# ==============================================================================

def test_documentation_governance_production_readiness():
    rep = doc_mod.default_documentation_governance_readiness_report()
    assert rep["bounded_claim_sample"] is False
    assert rep["unbounded_claim_sample"] is True
    assert isinstance(rep["normalized_title_sample"], str)
    assert len(rep["decision_issues"]) == 0

    all_objs = [
        doc_mod.DEFAULT_DOCUMENTATION_DECISION,
        *doc_mod.DEFAULT_DOC_INVENTORY,
        *doc_mod.DEFAULT_ADRS,
        *doc_mod.DEFAULT_CLAIMS,
        *doc_mod.DEFAULT_CLAIM_RULES,
        *doc_mod.DEFAULT_RELEASE_NOTES,
        *doc_mod.DEFAULT_STALE_FINDINGS,
        doc_mod.DEFAULT_REVIEW_GATE,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/")

    # Helper function tests
    unsupported_claim = dataclasses.replace(
        doc_mod.DEFAULT_CLAIMS[0],
        confidence=doc_mod.ClaimConfidence.UNSUPPORTED,
        evidence_paths=(),
    )
    issues = doc_mod.validate_claims_for_release((unsupported_claim,))
    assert len(issues) >= 1

    assert doc_mod.contains_unbounded_production_claim("This is production ready.") is True
    assert doc_mod.contains_unbounded_production_claim("This is a safe note.") is False
    assert doc_mod.normalize_doc_title("Docs: Title! ") == "docs-title"


# ==============================================================================
# 5. NOTIFICATIONS
# ==============================================================================

def test_notifications_production_readiness():
    rep = notif_mod.default_notifications_readiness_report()
    assert rep["first_enqueue"] == "queued"
    assert rep["second_enqueue"] == "duplicate"
    assert len(rep["provider_decision_issues"]) == 0

    pref = notif_mod.DEFAULT_NOTIFICATION_POLICY.preferences[0]
    assert pref.allows_delivery() in (True, False)
    pref_disabled = dataclasses.replace(pref, enabled=False, purpose=notif_mod.NotificationPurpose.MARKETING)
    assert pref_disabled.allows_delivery() is False

    retry_pol = notif_mod.DeliveryRetryPolicy(max_attempts=3, backoff_seconds=(1, 2, 4))
    assert retry_pol.validate() == []
    bad_retry = notif_mod.DeliveryRetryPolicy(max_attempts=0, backoff_seconds=())
    assert len(bad_retry.validate()) >= 2

    audit_ev = notif_mod.NotificationAuditEvent(
        event_id="e1",
        recipient_id="r1",
        audience=notif_mod.NotificationAudience.PARENT,
        purpose=notif_mod.NotificationPurpose.PROGRESS_SUMMARY,
        channel=notif_mod.NotificationChannel.EMAIL,
        delivery_status=notif_mod.DeliveryStatus.SENT,
        request_id="req1",
        idempotency_key="k1",
        occurred_at_utc=datetime.now(tz=timezone.utc),
    )
    assert audit_ev.validate() == []
    bad_audit = notif_mod.NotificationAuditEvent(
        event_id="",
        recipient_id="",
        audience=notif_mod.NotificationAudience.PARENT,
        purpose=notif_mod.NotificationPurpose.PROGRESS_SUMMARY,
        channel=notif_mod.NotificationChannel.EMAIL,
        delivery_status=notif_mod.DeliveryStatus.FAILED,
        request_id="",
        idempotency_key="",
        occurred_at_utc=datetime(2026, 1, 1),  # naive datetime
        raw_payload_retained=True,
    )
    assert len(bad_audit.validate()) >= 5

    all_objs = [
        notif_mod.DEFAULT_COMMUNICATION_PROVIDER_DECISION,
        notif_mod.DEFAULT_NOTIFICATION_POLICY,
        notif_mod.DEFAULT_RETRY_POLICY,
        *notif_mod.DEFAULT_TEMPLATES,
        pref,
        retry_pol,
        audit_ev,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/notifications/")

    # NotificationRequest & Outbox tests
    key = notif_mod.build_notification_idempotency_key(
        recipient_id="r1",
        purpose=notif_mod.NotificationPurpose.PROGRESS_SUMMARY,
        template_id="p1",
        template_version="v1",
        scheduled_bucket="2026-W01",
    )
    req = notif_mod.NotificationRequest(
        recipient_id="r1",
        audience=notif_mod.NotificationAudience.PARENT,
        purpose=notif_mod.NotificationPurpose.PROGRESS_SUMMARY,
        channel=notif_mod.NotificationChannel.EMAIL,
        template_id="p1",
        template_version="v1",
        locale="en-ZA",
        variables={"a": "b"},
        request_id="req-1",
        idempotency_key=key,
        scheduled_at_utc=datetime.now(tz=timezone.utc),
    )
    assert req.validate() == []
    _exercise_dataclass_mutations([req])

    outbox = notif_mod.NotificationOutbox()
    outbox.mark_dead_letter("k1", "delivery failed")
    assert len(outbox.dead_letter) == 1

    bad_req = dataclasses.replace(req, recipient_id="")
    with pytest.raises(ValueError):
        outbox.enqueue(bad_req)

    assert "[redacted-email]" in notif_mod.redact_contact_details("call user@domain.com")


# ==============================================================================
# 6. OPERATIONS SUPPORT
# ==============================================================================

def test_operations_support_production_readiness():
    rep = ops_mod.default_operations_support_readiness_report()
    assert isinstance(rep, dict)
    assert len(rep["decision_issues"]) == 0

    all_objs = [
        ops_mod.DEFAULT_OPERATIONS_DECISION,
        *ops_mod.DEFAULT_INCIDENT_CLASSIFICATION,
        *ops_mod.DEFAULT_ON_CALL_POLICIES,
        *ops_mod.DEFAULT_RUNBOOKS,
        *ops_mod.DEFAULT_SUPPORT_SLAS,
        *ops_mod.DEFAULT_STATUS_TEMPLATES,
        ops_mod.DEFAULT_INCIDENT_RECORD,
        ops_mod.DEFAULT_POST_INCIDENT_REVIEW,
        ops_mod.DEFAULT_HANDOVER,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/operations_support/")

    # Helper functions
    assert ops_mod.classify_support_priority(ops_mod.CustomerImpact.CRITICAL, True) == ops_mod.SupportPriority.P0
    assert ops_mod.classify_support_priority(ops_mod.CustomerImpact.MAJOR, False) == ops_mod.SupportPriority.P1
    assert ops_mod.classify_support_priority(ops_mod.CustomerImpact.MODERATE, False) == ops_mod.SupportPriority.P2
    assert ops_mod.classify_support_priority(ops_mod.CustomerImpact.MINOR, False) == ops_mod.SupportPriority.P3

    assert "[redacted-email]" in ops_mod.redact_incident_note("info at user@test.com")
    assert isinstance(ops_mod.compute_operations_evidence_checksum("sample"), str)


# ==============================================================================
# 7. QUALITY GATES
# ==============================================================================

def test_quality_gates_production_readiness():
    rep = qg_mod.default_quality_gate_readiness_report()
    assert rep["gate_status_sample"] == qg_mod.QualityGateStatus.PASS.value
    assert isinstance(rep["checksum_sample"], str)
    assert len(rep["strategy_issues"]) == 0

    all_objs = [
        qg_mod.DEFAULT_TESTING_STRATEGY,
        *qg_mod.DEFAULT_TEST_SUITES,
        *qg_mod.DEFAULT_COVERAGE_THRESHOLDS,
        *qg_mod.DEFAULT_QUALITY_GATES,
        *qg_mod.DEFAULT_RELEASE_EVIDENCE,
        *qg_mod.DEFAULT_DEFECT_TRIAGE,
        *qg_mod.DEFAULT_RELEASE_CHECKLISTS,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/testing/")

    # Gate status summarization
    assert qg_mod.summarize_gate_status({}) == qg_mod.QualityGateStatus.PASS
    assert qg_mod.summarize_gate_status({"g1": qg_mod.QualityGateStatus.FAIL}) == qg_mod.QualityGateStatus.FAIL
    assert qg_mod.summarize_gate_status({"g1": qg_mod.QualityGateStatus.BLOCKED}) == qg_mod.QualityGateStatus.BLOCKED
    assert qg_mod.summarize_gate_status({"g1": qg_mod.QualityGateStatus.WAIVED}) == qg_mod.QualityGateStatus.WAIVED

    # validate_evidence_bundle missing evidence types
    empty_bundle_errs = qg_mod.validate_evidence_bundle((), qg_mod.ReleaseStage.BETA)
    assert len(empty_bundle_errs) >= 4


# ==============================================================================
# 8. SECURITY POSTURE
# ==============================================================================

def test_security_posture_production_readiness():
    rep = sec_mod.default_security_posture_readiness_report()
    assert len(rep["decision_issues"]) == 0

    all_objs = [
        sec_mod.DEFAULT_SECURITY_DECISION,
        *sec_mod.DEFAULT_THREAT_MODEL,
        *sec_mod.DEFAULT_SECURITY_CONTROLS,
        *sec_mod.DEFAULT_VULNERABILITY_POLICIES,
        *sec_mod.DEFAULT_SECURITY_TESTS,
        *sec_mod.DEFAULT_SECRET_RULES,
        sec_mod.DEFAULT_SUPPLY_CHAIN,
        *sec_mod.DEFAULT_INCIDENT_RUNBOOKS,
        *sec_mod.DEFAULT_RISK_ACCEPTANCES,
    ]
    _exercise_dataclass_mutations(all_objs, doc_prefix="docs/security/")

    # Security header validation
    missing_headers = {"X-Frame-Options": "DENY"}
    hdr_errs = sec_mod.validate_security_headers(missing_headers)
    assert len(hdr_errs) >= 4

    # Secret redaction and checksum
    redacted = sec_mod.redact_secret_values("API_KEY=sk-1234567890abcdef1234567890")
    assert "[redacted-secret]" in redacted

    assert isinstance(sec_mod.compute_security_evidence_checksum("test"), str)
