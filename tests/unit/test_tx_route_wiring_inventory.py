from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.tx_route_wiring_inventory import ROUTE_FILES, build_inventory, write_inventory


ROOT = Path(__file__).resolve().parents[2]


def test_tx_route_wiring_scans_critical_route_files():
    assert {"auth", "popia", "diagnostics", "lessons"}.issubset(ROUTE_FILES)

    inventory = build_inventory()
    domains = {row.domain for row in inventory.routes}

    assert {"auth", "popia", "diagnostics", "lessons"}.intersection(domains)


def test_tx_route_wiring_inventory_marks_status_honestly():
    inventory = build_inventory()

    assert inventory.status in {
        "production-route-transaction-wiring-not-proven",
        "production-route-transaction-markers-present",
    }
    assert "isolated rollback proof services do not prove production route wiring" in inventory.remaining_boundaries


def test_tx_route_wiring_inventory_writes_reports():
    inventory = write_inventory()

    assert (ROOT / "docs/architecture/tx_route_wiring_inventory.json").exists()
    assert (ROOT / "docs/architecture/tx_route_wiring_inventory.md").exists()
    assert inventory.routes


def test_tx_route_wiring_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_tx_route_wiring.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_tx_route_wiring_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "tx-route-wiring-inventory:" in source
    assert "tx-route-wiring-check:" in source
    assert "backend-implementation-1751-1790-full-check:" in source
