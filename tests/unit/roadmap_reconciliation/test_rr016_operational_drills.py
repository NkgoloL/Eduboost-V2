from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.roadmap_reconciliation.verify_rr016_operational_drills import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    dst = tmp_path / "repo"
    paths = [
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_015_external_approvals_record.json",
        "docs/roadmap/reconciliation/rr_016_operational_drills.md",
        "docs/roadmap/reconciliation/rr_016_operational_drills_record.json",
        "docs/operations/drills/rr016_operational_drills_manifest.json",
        "docs/operations/drills/rr016_operational_drills_policy.md",
        "docs/operations/drills/rr016_backup_drill_report.template.md",
        "docs/operations/drills/rr016_restore_drill_report.template.md",
        "docs/operations/drills/rr016_rollback_drill_report.template.md",
        "docs/operations/drills/rr016_monitoring_dashboard_verification.template.md",
        "docs/operations/drills/rr016_incident_handoff_verification.template.md",
    ]
    for rel in paths:
        src = root / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    return dst


def _write_final_reports(repo: Path) -> None:
    base = repo / "docs" / "operations" / "drills"
    boundary = """
Billing launch authorised: false
Live payment processing authorised: false
Production release authorised: false
Deployment authorised: false
Release tag authorised: false
Public beta authorised: false
Public beta live traffic authorised: false
Runtime KG implementation claimed: false
"""
    reports = {
        "rr016_backup_drill_report.md": "Backup drill completed: true\nBackup evidence captured: true\n",
        "rr016_restore_drill_report.md": "Restore drill completed: true\nRestore verification completed: true\n",
        "rr016_rollback_drill_report.md": "Rollback drill completed: true\nRollback execution path verified: true\n",
        "rr016_monitoring_dashboard_verification.md": "Monitoring dashboard verified: true\nSLO panels verified: true\n",
        "rr016_incident_handoff_verification.md": "Incident handoff verified: true\nEscalation path verified: true\n",
    }
    for name, body in reports.items():
        (base / name).write_text(body + boundary, encoding="utf-8")


def test_rr016_authority_is_valid_before_capture() -> None:
    result = evaluate(Path.cwd())
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["operational_drills_recorded"] is False


def test_rr016_record_requires_boundaries_false(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "reconciliation" / "rr_016_operational_drills_record.json"
    data = json.loads(record_path.read_text())
    data["production_release_authorised"] = True
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert any("production_release_authorised" in error for error in result["errors"])


def test_rr016_requires_rr015_dependency(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    rr015 = repo / "docs" / "roadmap" / "reconciliation" / "rr_015_external_approvals_record.json"
    rr015.unlink()
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert result["rr015_external_approvals_valid"] is False


def test_rr016_final_reports_are_required_after_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "reconciliation" / "rr_016_operational_drills_record.json"
    data = json.loads(record_path.read_text())
    data.update({
        "operational_drills_recorded": True,
        "rr015_external_approvals_valid": True,
        "backup_drill_completed": True,
        "restore_drill_completed": True,
        "rollback_drill_completed": True,
        "monitoring_dashboard_verified": True,
        "incident_handoff_verified": True,
    })
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["valid"] is False
    assert any("final drill evidence failed" in error for error in result["errors"])


def test_rr016_valid_after_final_reports_and_record(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    _write_final_reports(repo)
    record_path = repo / "docs" / "roadmap" / "reconciliation" / "rr_016_operational_drills_record.json"
    data = json.loads(record_path.read_text())
    data.update({
        "operational_drills_recorded": True,
        "rr015_external_approvals_valid": True,
        "backup_drill_completed": True,
        "restore_drill_completed": True,
        "rollback_drill_completed": True,
        "monitoring_dashboard_verified": True,
        "incident_handoff_verified": True,
    })
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["valid"] is True
    assert result["backup_drill_completed"] is True
