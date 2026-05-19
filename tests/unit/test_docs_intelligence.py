from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.docs_inventory import IMPORTANT_DOCS, build_inventory, write_inventory


ROOT = Path(__file__).resolve().parents[2]


def test_docs_inventory_includes_recent_release_and_architecture_docs():
    inventory = build_inventory()
    paths = {item.path for item in inventory.documents}

    assert "docs/release/evidence_status_registry.yml" in paths
    assert "docs/release/ci_evidence.md" in paths
    assert "docs/architecture/transaction_boundary_inventory.md" in paths or "docs/architecture/transaction_boundary_inventory.json" in paths


def test_docs_inventory_writes_expected_artifacts():
    inventory = write_inventory()

    assert inventory.document_count > 0
    assert (ROOT / "docs/docs_inventory.json").exists()
    assert (ROOT / "docs/docs_inventory.md").exists()
    assert (ROOT / "docs/docs_gap_report.md").exists()

    payload = json.loads((ROOT / "docs/docs_inventory.json").read_text(encoding="utf-8"))
    assert payload["document_count"] == inventory.document_count


def test_docs_inventory_check_passes_after_write():
    subprocess.run(
        [sys.executable, "scripts/docs_inventory.py", "--write"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "scripts/docs_inventory.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_required_important_docs_list_tracks_release_gate_files():
    assert "docs/release/evidence_status_registry.yml" in IMPORTANT_DOCS
    assert "docs/release/ci_evidence.md" in IMPORTANT_DOCS
    assert "docs/release/transaction_rollback_rollup_report.md" in IMPORTANT_DOCS


def test_docs_intelligence_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_docs_intelligence.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout
