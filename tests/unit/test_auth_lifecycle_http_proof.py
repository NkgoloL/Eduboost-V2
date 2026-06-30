from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_lifecycle_http_proof import TARGETS, build_status, registered_routes, write_status

ROOT = Path(__file__).resolve().parents[2]


def test_auth_lifecycle_targets_are_complete():
    assert set(TARGETS) == {"register", "login", "refresh", "logout", "revoke_all_tokens"}


def test_auth_router_imports_and_registers_synthetically():
    router_import_ok, registration_ok, routes = registered_routes()
    assert router_import_ok
    assert registration_ok
    for function in TARGETS:
        assert function in routes


def test_auth_lifecycle_http_route_proof_passing():
    status = build_status()
    assert status.status == "auth-lifecycle-http-route-proof-passing"
    assert all(proof.passed for proof in status.proofs)


def test_auth_lifecycle_http_proof_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/auth_lifecycle_http_proof_status.json").exists()
    assert (ROOT / "docs/release/auth_lifecycle_http_proof_status.md").exists()
    assert status.status == "auth-lifecycle-http-route-proof-passing"


def test_auth_lifecycle_http_proof_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_lifecycle_http_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_auth_lifecycle_http_proof_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_auth_lifecycle_http_proof_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_lifecycle_http_proof_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-lifecycle-http-proof-status:" in source
    assert "auth-lifecycle-http-proof-check:" in source
    assert "backend-implementation-2591-2630-full-check:" in source
