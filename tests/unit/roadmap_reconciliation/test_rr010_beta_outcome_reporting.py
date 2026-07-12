from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


def _load_verifier(root: Path):
    module_path = root / "scripts/roadmap_reconciliation/verify_rr010_beta_outcome_reporting.py"
    spec = importlib.util.spec_from_file_location("verify_rr010", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(root))
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)
    return module


def _write_final_outcome_files(root: Path) -> None:
    outcome_dir = root / "docs/beta_outcomes"
    (outcome_dir / "rr010_beta_outcome_report.md").write_text(
        """# RR-010 Beta Outcome Report\n\nBeta outcome report completed: true\nMinimum beta duration met: true\nCohort size requirement met: true\nWeekly health reviews completed: true\nBeta outcome reporting complete: true\nProduction release authorised: false\nPublic beta authorised: false\nRuntime KG implementation claimed: false\n""",
        encoding="utf-8",
    )
    (outcome_dir / "rr010_weekly_health_reviews.md").write_text(
        """# RR-010 Weekly Health Reviews\n\nWeekly beta health reviews completed: true\nMinimum weekly review cadence met: true\n""",
        encoding="utf-8",
    )
    (outcome_dir / "rr010_educator_feedback_summary.md").write_text(
        """# RR-010 Educator Feedback Summary\n\nEducator feedback collected: true\nEducator content approval threshold met: true\n""",
        encoding="utf-8",
    )
    (outcome_dir / "rr010_incident_summary.md").write_text(
        """# RR-010 Incident Summary\n\nZero critical security incidents: true\nZero PII exposure events: true\nZero consent incidents: true\n""",
        encoding="utf-8",
    )
    metrics = {
        "rr_id": "RR-010",
        "cohort_size": 20,
        "beta_duration_days": 28,
        "uptime_percent": 99.5,
        "p95_diagnostic_latency_seconds": 2.0,
        "educator_content_approval_percent": 80,
        "learner_session_completion_percent": 70,
        "backup_restore_drill_count": 2,
        "weekly_health_review_count": 4,
        "critical_security_incidents": 0,
        "pii_exposure_events": 0,
        "consent_incidents": 0,
        "minimum_beta_duration_met": True,
        "cohort_size_requirement_met": True,
        "educator_feedback_collected": True,
        "uptime_target_met": True,
        "p95_diagnostic_latency_target_met": True,
        "zero_critical_security_incidents": True,
        "zero_pii_exposure_events": True,
        "zero_consent_incidents": True,
        "educator_content_approval_threshold_met": True,
        "learner_session_completion_threshold_met": True,
        "backup_restore_drill_references_recorded": True,
        "weekly_health_reviews_completed": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
    }
    (outcome_dir / "rr010_beta_metrics_summary.json").write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")


def test_rr010_authority_files_are_valid() -> None:
    root = Path.cwd()
    verifier = _load_verifier(root)
    result = verifier.evaluate(root)
    assert result["authority_valid"] is True, result
    assert result["valid"] is True, result


def _copy_rr010_minimal_repo(source: Path, target: Path) -> None:
    paths = [
        "Makefile",
        ".github/workflows/rr010-beta-outcome-reporting.yml",
        "scripts/beta_outcomes/audit_rr010_beta_outcome_reporting.py",
        "scripts/roadmap_reconciliation/verify_rr010_beta_outcome_reporting.py",
        "scripts/roadmap_reconciliation/capture_rr010_beta_outcome_reporting_evidence.py",
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_009_governance_process_reconciliation_record.json",
        "docs/roadmap/reconciliation/rr_010_beta_outcome_reporting.md",
        "docs/roadmap/reconciliation/rr_010_beta_outcome_reporting_record.json",
    ]
    for rel in paths:
        src = source / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copytree(source / "docs/beta_outcomes", target / "docs/beta_outcomes", dirs_exist_ok=True)


def test_rr010_record_becomes_valid_after_final_outcome_files_and_capture_shape(tmp_path: Path) -> None:
    source = Path.cwd()
    target = tmp_path / "repo"
    _copy_rr010_minimal_repo(source, target)
    _write_final_outcome_files(target)
    verifier = _load_verifier(target)
    record_path = target / "docs/roadmap/reconciliation/rr_010_beta_outcome_reporting_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record.update(
        {
            "beta_outcome_reporting_recorded": True,
            "minimum_beta_duration_met": True,
            "cohort_size_requirement_met": True,
            "educator_feedback_collected": True,
            "uptime_target_met": True,
            "p95_diagnostic_latency_target_met": True,
            "zero_critical_security_incidents": True,
            "zero_pii_exposure_events": True,
            "zero_consent_incidents": True,
            "educator_content_approval_threshold_met": True,
            "learner_session_completion_threshold_met": True,
            "backup_restore_drill_references_recorded": True,
            "weekly_health_reviews_completed": True,
            "beta_outcome_report_recorded": True,
            "rr003_fallback_coverage_caveat_visible": True,
            "rr006_non_required_checks_caveat_visible": True,
            "rr015_external_approvals_remaining_visible": True,
            "rr016_operational_drills_remaining_visible": True,
            "beta_outcome_audit": {"valid": True, "final_outputs_valid": True},
        }
    )
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    result = verifier.evaluate(target)
    assert result["valid"] is True, result


def test_rr010_audit_rejects_missing_final_files_when_required(tmp_path: Path) -> None:
    source = Path.cwd()
    root = tmp_path / "repo"
    _copy_rr010_minimal_repo(source, root)
    for path in (
        "rr010_beta_outcome_report.md",
        "rr010_beta_metrics_summary.json",
        "rr010_weekly_health_reviews.md",
        "rr010_educator_feedback_summary.md",
        "rr010_incident_summary.md",
    ):
        (root / "docs/beta_outcomes" / path).unlink()
    audit_path = root / "scripts/beta_outcomes/audit_rr010_beta_outcome_reporting.py"
    spec = importlib.util.spec_from_file_location("audit_rr010", audit_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit(root, require_final=True)
    assert result["authority_valid"] is True, result
    assert result["final_outputs_valid"] is False
    assert any("missing final RR-010 outcome file" in error for error in result["errors"])


def test_rr010_policy_carries_caveats_and_boundaries() -> None:
    root = Path.cwd()
    policy = (root / "docs/beta_outcomes/rr010_beta_outcome_reporting_policy.md").read_text(encoding="utf-8")
    assert "RR-003" in policy
    assert "0.0" in policy
    assert "RR-006" in policy
    assert "non-required" in policy
    assert "RR-015" in policy
    assert "RR-016" in policy
    assert "public beta" in policy.lower()
    assert "not authorised" in policy
    assert "Runtime KG" in policy


def test_rr010_makefile_targets_exist() -> None:
    root = Path.cwd()
    text = (root / "Makefile").read_text(encoding="utf-8")
    assert "rr010-beta-outcome-audit" in text
    assert "rr010-beta-outcome-check" in text
