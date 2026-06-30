from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.transaction_boundary_inventory import generate_inventory, write_inventory

ROOT = Path(__file__).resolve().parents[2]


def test_transaction_boundary_inventory_generates_findings():
    inventory = generate_inventory()

    assert inventory.findings
    assert inventory.candidate_count >= 0
    assert "not-proven" in inventory.policy


def test_transaction_boundary_inventory_mentions_critical_domains():
    inventory = generate_inventory()
    blob = json.dumps([finding.__dict__ for finding in inventory.findings]).lower()

    for term in ["auth", "consent", "diagnostic", "lesson"]:
        assert term in blob


def test_transaction_boundary_inventory_writes_artifacts():
    inventory = generate_inventory()
    write_inventory(inventory)

    assert (ROOT / "docs/architecture/transaction_boundary_inventory.json").exists()
    assert (ROOT / "docs/architecture/transaction_boundary_inventory.md").exists()


def test_transaction_boundary_guardrail_script_runs():
    env = os.environ.copy()
    env["SKIP_PYTEST_RECURSION"] = "1"
    result = subprocess.run(
        [sys.executable, "scripts/check_transaction_boundary_guardrails.py"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_evidence_registry_tracks_tx_as_not_proven():
    registry = (ROOT / "docs/release/evidence_status_registry.yml").read_text(encoding="utf-8")

    assert "id: TX-001" in registry
    assert "proof_status: not-proven" in registry
    assert "rollback" in registry.lower()
