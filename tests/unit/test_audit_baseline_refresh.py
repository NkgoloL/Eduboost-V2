from __future__ import annotations

from pathlib import Path

from scripts.audit_baseline_refresh import (
    _evidence_marker_status,
    _surface_status,
    current_commit,
    write_status,
)


def test_surface_status_marks_current_commit_not_stale(tmp_path: Path):
    path = tmp_path / "surface.json"
    sha = "a" * 40
    path.write_text('{"current_commit": "' + sha + '", "status": "NO-GO"}', encoding="utf-8")
    surface = _surface_status("test", path, sha)
    assert surface.exists
    assert not surface.stale
    assert surface.commit == sha


def test_surface_status_marks_different_commit_stale(tmp_path: Path):
    path = tmp_path / "surface.json"
    path.write_text('{"current_commit": "' + ("b" * 40) + '", "status": "NO-GO"}', encoding="utf-8")
    surface = _surface_status("test", path, "a" * 40)
    assert surface.exists
    assert surface.stale


def test_evidence_marker_status_detects_marker(tmp_path: Path):
    path = tmp_path / "evidence.json"
    path.write_text('{"status": "ci-evidence-accepted"}', encoding="utf-8")
    marker = _evidence_marker_status("CI-001", path, "ci-evidence-accepted")
    assert marker.exists
    assert marker.accepted


def test_audit_baseline_refresh_writes_status_files():
    status = write_status()
    assert status.current_commit == current_commit()
    assert status.beta_decision in {"GO", "NO-GO"}
    assert Path("docs/release/audit_baseline_refresh_status.json").exists()
    assert Path("docs/release/audit_baseline_refresh_status.md").exists()
    assert Path("docs/release/release_go_no_go_status.json").exists()
    assert Path("docs/release/release_go_no_go_status.md").exists()
