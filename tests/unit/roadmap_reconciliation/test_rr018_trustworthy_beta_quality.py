from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.roadmap_reconciliation.verify_rr018_trustworthy_beta_quality import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    dst = tmp_path / "repo"
    paths = [
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_017_release_safety_controls_record.json",
        "docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality.md",
        "docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality_record.json",
        "docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_manifest.json",
        "docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_policy.md",
        "docs/product_quality/trustworthy_beta/rr018_feedback_report_issue_validation.template.md",
        "docs/product_quality/trustworthy_beta/rr018_content_correction_workflow.template.md",
        "docs/product_quality/trustworthy_beta/rr018_human_review_queue.template.md",
        "docs/product_quality/trustworthy_beta/rr018_educator_caps_priority_review.template.md",
        "docs/product_quality/trustworthy_beta/rr018_trustworthy_beta_quality_boundary.template.md",
        "app/frontend/src/components/eduboost/TrustworthyBetaQualityPanel.tsx",
        "app/frontend/__tests__/TrustworthyBetaQualityPanel.test.tsx",
        "app/domain/trustworthy_beta_quality.py",
        "app/services/trustworthy_beta_quality.py",
    ]
    for rel in paths:
        src = root / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)

    record_path = dst / "docs" / "roadmap" / "reconciliation" / "rr_018_trustworthy_beta_product_quality_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    data.update({
        "trustworthy_beta_product_quality_recorded": False,
        "rr017_release_safety_controls_valid": False,
        "feedback_report_issue_button_validated": False,
        "content_correction_workflow_recorded": False,
        "human_review_queue_recorded": False,
        "educator_caps_priority_review_recorded": False,
        "content_correction_sla_recorded": False,
        "guardian_feedback_privacy_boundary_recorded": False,
        "no_learner_pii_in_feedback_evidence": False,
        "trustworthy_beta_quality_boundary_recorded": False,
        "all_reconciled_rr_items_addressed_through_rr018": False,
        "billing_launch_authorised": False,
        "live_payment_processing_authorised": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "public_beta_live_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
    })
    record_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dst


def _write_final_quality_files(repo: Path) -> None:
    base = repo / "docs" / "product_quality" / "trustworthy_beta"
    common = """
Feedback/report issue button validated: true
Content correction workflow recorded: true
Human review queue recorded: true
Educator CAPS priority review recorded: true
Content correction SLA recorded: true
Guardian/learner feedback privacy boundary recorded: true
No learner PII in feedback evidence: true

Billing launch authorised: false
Live payment processing authorised: false
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Public beta authorised: false
Public beta live traffic authorised: false
Runtime KG implementation claimed: false
"""
    files = {
        "rr018_feedback_report_issue_validation.md": "Feedback/report issue button validated: true\n",
        "rr018_content_correction_workflow.md": "Content correction workflow recorded: true\n",
        "rr018_human_review_queue.md": "Human review queue recorded: true\n",
        "rr018_educator_caps_priority_review.md": "Educator CAPS priority review recorded: true\n",
        "rr018_trustworthy_beta_quality_boundary.md": "Trustworthy beta quality boundary recorded: true\n",
    }
    for name, body in files.items():
        (base / name).write_text(body + common, encoding="utf-8")


def _mark_record_captured(repo: Path) -> None:
    record_path = repo / "docs" / "roadmap" / "reconciliation" / "rr_018_trustworthy_beta_product_quality_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    data.update({
        "trustworthy_beta_product_quality_recorded": True,
        "rr017_release_safety_controls_valid": True,
        "feedback_report_issue_button_validated": True,
        "content_correction_workflow_recorded": True,
        "human_review_queue_recorded": True,
        "educator_caps_priority_review_recorded": True,
        "content_correction_sla_recorded": True,
        "guardian_feedback_privacy_boundary_recorded": True,
        "no_learner_pii_in_feedback_evidence": True,
        "trustworthy_beta_quality_boundary_recorded": True,
        "rr003_fallback_coverage_caveat_visible": True,
        "rr006_non_required_checks_caveat_visible": True,
        "rr016_clean_git_state_caveat_visible": True,
        "rr017_release_safety_controls_boundary_visible": True,
        "all_reconciled_rr_items_addressed_through_rr018": True,
    })
    record_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_rr018_authority_is_valid_before_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    result = evaluate(repo)
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["trustworthy_beta_product_quality_recorded"] is False


def test_rr018_requires_rr017_dependency(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    rr017 = repo / "docs" / "roadmap" / "reconciliation" / "rr_017_release_safety_controls_record.json"
    rr017.unlink()
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert result["rr017_release_safety_controls_valid"] is False


def test_rr018_boundary_flags_must_remain_false(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "reconciliation" / "rr_018_trustworthy_beta_product_quality_record.json"
    data = json.loads(record_path.read_text())
    data["public_beta_authorised"] = True
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert any("public_beta_authorised" in error for error in result["errors"])


def test_rr018_final_files_are_required_after_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    _mark_record_captured(repo)
    result = evaluate(repo)
    assert result["valid"] is False
    assert any("final trustworthy-beta quality evidence failed" in error for error in result["errors"])


def test_rr018_valid_after_final_files_and_record(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    _write_final_quality_files(repo)
    _mark_record_captured(repo)
    result = evaluate(repo)
    assert result["valid"] is True
    assert result["feedback_report_issue_button_validated"] is True
    assert result["human_review_queue_recorded"] is True
    assert result["all_reconciled_rr_items_addressed_through_rr018"] is True


def test_rr018_boundary_flags_are_emitted_as_false_values(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    _write_final_quality_files(repo)
    _mark_record_captured(repo)
    result = evaluate(repo)
    assert result["billing_launch_authorised"] is False
    assert result["public_beta_authorised"] is False
    assert result["runtime_kg_implementation_claimed"] is False
