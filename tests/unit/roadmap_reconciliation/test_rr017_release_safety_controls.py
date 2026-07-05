from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.roadmap_reconciliation.verify_rr017_release_safety_controls import evaluate


def _copy_repo(tmp_path: Path) -> Path:
    root = Path.cwd()
    dst = tmp_path / "repo"
    paths = [
        "docs/roadmap/reconciliation/outstanding_work_register.md",
        "docs/roadmap/reconciliation/rr_016_operational_drills_record.json",
        "docs/roadmap/reconciliation/rr_017_release_safety_controls.md",
        "docs/roadmap/reconciliation/rr_017_release_safety_controls_record.json",
        "docs/release_safety/rr017_release_safety_controls_manifest.json",
        "docs/release_safety/rr017_release_safety_controls_policy.md",
        "docs/release_safety/rr017_release_safety_control_attestation.template.md",
        "docs/release_safety/rr017_prohibited_operations_register.template.md",
        "docs/release_safety/rr017_migration_window_control.template.md",
        "docs/release_safety/rr017_health_probe_immutability_validation.template.md",
        "docs/release_safety/rr017_release_change_control_boundary.template.md",
    ]
    for rel in paths:
        src = root / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)

    record_path = dst / "docs" / "roadmap" / "reconciliation" / "rr_017_release_safety_controls_record.json"
    data = json.loads(record_path.read_text(encoding="utf-8"))
    data.update({
        "release_safety_controls_recorded": False,
        "rr016_operational_drills_valid": False,
        "release_safety_controls_attested": False,
        "destructive_audit_consent_db_changes_blocked": False,
        "alembic_stamp_head_repair_blocked": False,
        "production_db_mutation_requires_migration_window": False,
        "mutating_health_probes_blocked": False,
        "prohibited_operations_register_recorded": False,
        "migration_window_control_recorded": False,
        "health_probe_immutability_validated": False,
        "release_change_control_boundary_recorded": False,
        "break_glass_exception_process_recorded": False,
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


def _write_final_reports(repo: Path) -> None:
    base = repo / "docs" / "release_safety"
    controls = """
Destructive audit consent DB changes blocked: true
Alembic stamp head repair blocked: true
Production DB mutation requires migration window: true
Mutating health probes blocked: true
Break-glass exception process recorded: true
"""
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
        "rr017_release_safety_control_attestation.md": "Release safety controls attested: true\n",
        "rr017_prohibited_operations_register.md": "Prohibited operations register recorded: true\n",
        "rr017_migration_window_control.md": "Migration window control recorded: true\n",
        "rr017_health_probe_immutability_validation.md": "Health probe immutability validated: true\n",
        "rr017_release_change_control_boundary.md": "Release change-control boundary recorded: true\n",
    }
    for name, body in reports.items():
        (base / name).write_text(body + controls + boundary, encoding="utf-8")


def _mark_record_captured(repo: Path) -> None:
    record_path = repo / "docs" / "roadmap" / "reconciliation" / "rr_017_release_safety_controls_record.json"
    data = json.loads(record_path.read_text())
    data.update({
        "release_safety_controls_recorded": True,
        "rr016_operational_drills_valid": True,
        "release_safety_controls_attested": True,
        "destructive_audit_consent_db_changes_blocked": True,
        "alembic_stamp_head_repair_blocked": True,
        "production_db_mutation_requires_migration_window": True,
        "mutating_health_probes_blocked": True,
        "prohibited_operations_register_recorded": True,
        "migration_window_control_recorded": True,
        "health_probe_immutability_validated": True,
        "release_change_control_boundary_recorded": True,
        "break_glass_exception_process_recorded": True,
        "rr003_fallback_coverage_caveat_visible": True,
        "rr006_non_required_checks_caveat_visible": True,
        "rr016_clean_git_state_caveat_visible": True,
        "rr018_trustworthy_beta_quality_remaining_visible": True,
    })
    record_path.write_text(json.dumps(data), encoding="utf-8")


def test_rr017_authority_is_valid_before_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    result = evaluate(repo)
    assert result["authority_valid"] is True
    assert result["valid"] is False
    assert result["release_safety_controls_recorded"] is False


def test_rr017_requires_rr016_dependency(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    rr016 = repo / "docs" / "roadmap" / "reconciliation" / "rr_016_operational_drills_record.json"
    rr016.unlink()
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert result["rr016_operational_drills_valid"] is False


def test_rr017_boundary_flags_must_remain_false(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    record_path = repo / "docs" / "roadmap" / "reconciliation" / "rr_017_release_safety_controls_record.json"
    data = json.loads(record_path.read_text())
    data["production_release_authorised"] = True
    record_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(repo)
    assert result["authority_valid"] is False
    assert any("production_release_authorised" in error for error in result["errors"])


def test_rr017_final_reports_are_required_after_capture(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    _mark_record_captured(repo)
    result = evaluate(repo)
    assert result["valid"] is False
    assert any("final release-safety evidence failed" in error for error in result["errors"])


def test_rr017_valid_after_final_reports_and_record(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    _write_final_reports(repo)
    _mark_record_captured(repo)
    result = evaluate(repo)
    assert result["valid"] is True
    assert result["destructive_audit_consent_db_changes_blocked"] is True
    assert result["mutating_health_probes_blocked"] is True


def test_rr017_boundary_flags_are_emitted_as_false_values(tmp_path: Path) -> None:
    repo = _copy_repo(tmp_path)
    _write_final_reports(repo)
    _mark_record_captured(repo)
    result = evaluate(repo)
    assert result["billing_launch_authorised"] is False
    assert result["production_release_authorised"] is False
    assert result["runtime_kg_implementation_claimed"] is False
