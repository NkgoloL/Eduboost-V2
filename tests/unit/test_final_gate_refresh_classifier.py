from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.final_gate_classifier import build_refresh, registry_findings, release_ready_for, write_refresh

ROOT = Path(__file__).resolve().parents[2]


def test_release_ready_classifier_accepts_integration_passing_none():
    assert release_ready_for("integration-passing", "none")
    assert release_ready_for("runtime-passing", "none")
    assert release_ready_for("production-ready", "none")


def test_release_ready_classifier_rejects_blocked_statuses():
    assert not release_ready_for("external-blocked", "none")
    assert not release_ready_for("not-proven", "none")
    assert not release_ready_for("scaffold-only", "none")


def test_release_ready_classifier_rejects_skipped_and_runtime_blockers():
    assert not release_ready_for("integration-passing", "skipped tests are not proof")
    assert not release_ready_for("runtime-passing", "live Redis worker enqueue/dequeue staging evidence")
    assert not release_ready_for("runtime-passing", "full HTTP and staging proof remains pending")


def test_auth_refresh_db_entries_are_release_ready_and_non_blocking_after_patch():
    findings = {finding.id: finding for finding in registry_findings()}
    for item_id in ["AUTH-REFRESH-DB-PROOF-001", "AUTH-REFRESH-DB-EVIDENCE-001"]:
        finding = findings[item_id]
        assert finding.proof_status == "integration-passing"
        assert finding.closure_blocker == "none"
        assert finding.release_ready
        assert not finding.effective_blocks_beta


def test_external_and_not_proven_items_remain_beta_blocking():
    refresh = build_refresh()
    beta_ids = {finding.id for finding in refresh.beta_critical_findings}
    for item_id in ["POPIA-001", "CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001", "EXT-GATE-001"]:
        assert item_id in beta_ids


def test_final_gate_refresh_status_writes_reports():
    refresh = write_refresh()
    assert (ROOT / "docs/release/final_beta_gate_refresh.json").exists()
    assert (ROOT / "docs/release/final_beta_gate_refresh.md").exists()
    assert refresh.beta_decision == "NO-GO"
    resolved_ids = {finding.id for finding in refresh.resolved_non_blocking_findings}
    assert "AUTH-REFRESH-DB-PROOF-001" in resolved_ids
    assert "AUTH-REFRESH-DB-EVIDENCE-001" in resolved_ids


def test_final_gate_refresh_classifier_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_final_gate_refresh_classifier.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_final_gate_refresh_classifier_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "final-gate-refresh-classifier-patch:" in source
    assert "final-gate-refresh-classifier-check:" in source
    assert "backend-implementation-2791-2830-full-check:" in source
