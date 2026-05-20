from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.evidence_attachment_runbook import COMMANDS, RELEASE_MODE_SEQUENCE, build_manifest, write_runbook

ROOT = Path(__file__).resolve().parents[2]

def test_evidence_attachment_runbook_tracks_required_blockers():
    ids = {command.id for command in COMMANDS}
    assert {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}.issubset(ids)
    assert {"ROUTE-TX-AUTH-001", "ROUTE-TX-POPIA-001", "ROUTE-TX-DIAG-001"}.issubset(ids)

def test_evidence_attachment_runbook_has_release_mode_sequence():
    assert "make final-gate-refresh-release-check" in RELEASE_MODE_SEQUENCE
    assert "make release-go-no-go-release-check" in RELEASE_MODE_SEQUENCE
    assert "make ci-run-evidence-release-check" in RELEASE_MODE_SEQUENCE

def test_evidence_attachment_runbook_manifest_builds():
    manifest = build_manifest()
    assert manifest.command_count == len(COMMANDS)
    assert manifest.no_false_closure_rules
    assert manifest.current_commit

def test_evidence_attachment_runbook_writes_artifacts():
    manifest = write_runbook()
    assert (ROOT / "docs/release/evidence_attachment_runbook.md").exists()
    assert (ROOT / "docs/release/evidence_attachment_runbook_manifest.json").exists()
    assert manifest.runbook_file == "docs/release/evidence_attachment_runbook.md"

def test_evidence_attachment_runbook_content_mentions_no_go_until_real_evidence():
    write_runbook()
    text = (ROOT / "docs/release/evidence_attachment_runbook.md").read_text(encoding="utf-8")
    assert "NO-GO" in text
    assert "not evidence by itself" in text
    assert "Do not replace real GitHub Actions evidence" in text

def test_evidence_attachment_runbook_registry_patcher_runs_directly():
    result = subprocess.run([sys.executable, "scripts/patch_evidence_attachment_runbook_registry.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    assert result.returncode == 0, result.stdout

def test_evidence_attachment_runbook_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run([sys.executable, "scripts/check_evidence_attachment_runbook.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}, check=False)
    assert result.returncode == 0, result.stdout

def test_makefile_contains_evidence_attachment_runbook_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "evidence-attachment-runbook:" in source
    assert "evidence-attachment-runbook-check:" in source
    assert "backend-implementation-2311-2350-full-check:" in source
