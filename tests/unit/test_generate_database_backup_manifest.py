from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.generate_database_backup_manifest import BackupManifestInput, render_manifest, stable_manifest_id


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_backup_manifest_id_is_stable() -> None:
    assert stable_manifest_id("abc") == stable_manifest_id("abc")
    assert stable_manifest_id("abc") != stable_manifest_id("def")


@pytest.mark.unit
def test_backup_manifest_renders_required_evidence() -> None:
    text = render_manifest(
        BackupManifestInput(
            backup_artifact_id="backup-001",
            target_environment="staging",
            retention_days=30,
            encrypted=True,
        )
    )

    assert "Database Backup Manifest" in text
    assert "backup-001" in text
    assert "backup artifact is encrypted" in text
    assert "make database-backup-dry-run" in text


@pytest.mark.unit
def test_backup_manifest_cli_writes_default_doc() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_database_backup_manifest.py", "--encrypted"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    doc = REPO_ROOT / "docs" / "operations" / "database_backup_manifest.md"
    assert doc.exists()
    assert "Database Backup Manifest" in doc.read_text(encoding="utf-8")


@pytest.mark.unit
def test_makefile_exposes_database_backup_manifest() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "database-backup-manifest:" in text
    assert "scripts/generate_database_backup_manifest.py --encrypted" in text
