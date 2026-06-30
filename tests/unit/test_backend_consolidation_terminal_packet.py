from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_manifest_generator_collects_required_paths():
    module = _load_module(
        "scripts/generate_backend_consolidation_evidence_manifest.py",
        "backend_consolidation_manifest_for_test",
    )
    assert "docs/release/backend_consolidation_terminal_packet.md" in module.EVIDENCE_PATHS
    rows = module.collect_rows()
    assert rows


def test_terminal_packet_contains_non_destructive_boundary():
    text = (ROOT / "docs/release/backend_consolidation_terminal_packet.md").read_text(encoding="utf-8")
    assert "does not authorize implementation or deletion" in text
    assert "release-owner approval for deletion" in text


def test_terminal_packet_checker_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_backend_consolidation_terminal_packet.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_terminal_report_generator_runs():
    result = subprocess.run(
        [sys.executable, "scripts/generate_backend_consolidation_terminal_report.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert (ROOT / "docs/release/backend_consolidation_terminal_report.md").exists()


def test_makefile_contains_terminal_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-consolidation-evidence-manifest:" in text
    assert "backend-consolidation-terminal-check:" in text
    assert "backend-consolidation-terminal-report:" in text
    assert "backend-consolidation-terminal-full-check:" in text
