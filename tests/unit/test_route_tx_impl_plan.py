from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.route_tx_impl_plan import build_plan, write_plan


ROOT = Path(__file__).resolve().parents[2]


def test_route_tx_impl_plan_builds_from_inventory():
    plan = build_plan()

    assert plan.source_inventory == "docs/architecture/tx_route_wiring_inventory.json"
    assert plan.plan_status in {
        "blocked-until-route-wiring-and-live-db-proof",
        "no-unproven-mutation-routes-detected",
    }
    assert plan.no_false_closure_rules


def test_route_tx_impl_plan_actions_require_live_db_proof_when_present():
    plan = build_plan()

    for action in plan.actions:
        assert action.live_db_proof_required is True
        assert action.can_be_closed_by_static_marker is False
        assert action.implementation_action
        assert action.negative_test_action


def test_route_tx_impl_plan_prioritizes_auth_and_popia_before_lower_risk_domains():
    plan = build_plan()
    priorities = {action.domain: action.priority for action in plan.actions}

    if "auth" in priorities:
        assert priorities["auth"] == "P0"
    if "popia" in priorities:
        assert priorities["popia"] == "P0"


def test_route_tx_impl_plan_writes_reports():
    plan = write_plan()

    assert (ROOT / "docs/release/route_transaction_implementation_plan.json").exists()
    assert (ROOT / "docs/release/route_transaction_implementation_plan.md").exists()
    assert plan.current_commit


def test_route_tx_impl_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_route_tx_impl_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_route_tx_impl_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_impl_plan.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_route_tx_impl_release_mode_fails_when_actions_remain():
    plan = build_plan()
    if plan.action_count == 0:
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_impl_plan.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires route transaction implementation actions to be zero" in result.stdout


def test_makefile_contains_route_tx_impl_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "route-tx-impl-plan:" in source
    assert "route-tx-impl-plan-check:" in source
    assert "backend-implementation-2031-2070-full-check:" in source
