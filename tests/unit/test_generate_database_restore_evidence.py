from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.generate_database_restore_evidence import RestoreEvidenceInput, render_evidence


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_restore_evidence_renders_required_sections() -> None:
    text = render_evidence(
        RestoreEvidenceInput(
            backup_artifact_id="backup-001",
            target_environment="staging",
            integrity_status="passed",
            learner_count_status="passed",
            consent_count_status="passed",
            audit_count_status="passed",
        )
    )

    assert "Database Restore Evidence" in text
    assert "backup-001" in text
    assert "Learner count status" in text
    assert "Consent count status" in text
    assert "Audit count status" in text
    assert "Production promotion is blocked" in text


@pytest.mark.unit
def test_restore_evidence_cli_writes_default_doc() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_database_restore_evidence.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    doc = REPO_ROOT / "docs" / "operations" / "database_restore_evidence.md"
    assert doc.exists()
    assert "Database Restore Evidence" in doc.read_text(encoding="utf-8")


@pytest.mark.unit
def test_makefile_exposes_database_restore_evidence() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "database-restore-evidence:" in text
    assert "scripts/generate_database_restore_evidence.py" in text
