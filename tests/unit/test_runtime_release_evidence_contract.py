from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]



def _contains_status_marker(text: str, marker: str) -> bool:
    return (
        marker in text
        or marker.replace("Status:", "**Status:**") in text
        or f"<!-- {marker} -->" in text
    )


def test_runtime_release_evidence_check_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_runtime_release_evidence.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_runtime_evidence_files_do_not_claim_completion_without_data():
    for relative in [
        "docs/release/migration_evidence.md",
        "docs/release/restore_drill_evidence.md",
        "docs/release/rollback_drill_evidence.md",
    ]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert _contains_status_marker(text, "Status: pending runtime execution")
        assert "TODO" in text


def test_makefile_contains_runtime_release_evidence_target():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "runtime-release-evidence-check:" in text
    assert "release-readiness-local-check:" in text
