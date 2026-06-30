from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.beta_no_go_handoff_packet import REQUIRED_EVIDENCE_ITEMS, build_packet, write_packet


ROOT = Path(__file__).resolve().parents[2]


def test_beta_no_go_handoff_tracks_required_evidence_items():
    assert {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}.issubset(REQUIRED_EVIDENCE_ITEMS)
    assert {"ROUTE-TX-AUTH-001", "ROUTE-TX-POPIA-001", "ROUTE-TX-DIAG-001"}.issubset(REQUIRED_EVIDENCE_ITEMS)


def test_beta_no_go_handoff_builds_packet():
    packet = build_packet()

    assert packet.beta_decision in {"GO", "NO-GO", "UNKNOWN"}
    assert packet.required_items
    assert packet.freeze_rules
    assert packet.no_false_closure_rules


def test_beta_no_go_handoff_required_items_are_not_locally_closeable():
    packet = build_packet()

    assert all(not item.local_close_allowed for item in packet.required_items)


def test_beta_no_go_handoff_writes_reports():
    packet = write_packet()

    assert (ROOT / "docs/release/beta_no_go_handoff_packet.json").exists()
    assert (ROOT / "docs/release/beta_no_go_handoff_packet.md").exists()
    assert packet.current_commit


def test_beta_no_go_handoff_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_beta_no_go_handoff_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_beta_no_go_handoff_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_beta_no_go_handoff_packet.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_beta_no_go_handoff_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "beta-no-go-handoff-packet:" in source
    assert "beta-no-go-handoff-check:" in source
    assert "backend-implementation-2351-2390-full-check:" in source
