from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from scripts.docs_inventory import IMPORTANT_DOCS, build_inventory, write_inventory


ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.governance


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
    import fcntl
    lock_path = ROOT / ".docs_inventory.lock"
    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            write_inventory()
            from scripts.docs_inventory import check_inventory
            errors = check_inventory()
            assert not errors, f"Docs inventory check errors: {errors}"
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def test_required_important_docs_list_tracks_release_gate_files():
    assert "docs/release/evidence_status_registry.yml" in IMPORTANT_DOCS
    assert "docs/release/ci_evidence.md" in IMPORTANT_DOCS
    assert "docs/release/transaction_rollback_rollup_report.md" in IMPORTANT_DOCS


def test_docs_intelligence_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    import fcntl
    lock_path = ROOT / ".docs_inventory.lock"
    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            from scripts.check_docs_intelligence import main as check_main
            old_skip = os.environ.get("SKIP_PYTEST_RECURSION")
            try:
                os.environ["SKIP_PYTEST_RECURSION"] = "1"
                ret = check_main()
                assert ret == 0
            finally:
                if old_skip is None:
                    os.environ.pop("SKIP_PYTEST_RECURSION", None)
                else:
                    os.environ["SKIP_PYTEST_RECURSION"] = old_skip
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
