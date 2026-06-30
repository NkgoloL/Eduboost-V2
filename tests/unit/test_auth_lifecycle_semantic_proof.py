from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_lifecycle_semantic_proof import (
    COOKIE_TARGETS,
    TARGETS,
    build_status,
    cookie_semantic_proofs,
    route_semantic_proofs,
    write_status,
)

ROOT = Path(__file__).resolve().parents[2]


def test_auth_lifecycle_semantic_targets_are_complete():
    assert set(TARGETS) == {"register", "login", "refresh", "logout", "revoke_all_tokens"}
    assert set(COOKIE_TARGETS) == {"logout", "revoke_all_tokens"}


def test_auth_lifecycle_routes_delegate_without_direct_cookie_or_token_logic():
    for proof in route_semantic_proofs():
        assert proof.delegates_to_service
        assert proof.has_auth_service_param
        assert proof.prohibited_route_calls == []


def test_logout_and_revoke_controlled_cookie_proof():
    for proof in cookie_semantic_proofs():
        assert proof.callable_ok
        assert "refresh_token" in proof.deleted_cookies
        assert proof.returned_mapping


def test_auth_lifecycle_semantic_status_passing():
    status = build_status()
    assert status.status == "auth-lifecycle-controlled-semantic-proof-passing"
    assert not status.blockers


def test_auth_lifecycle_semantic_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/auth_lifecycle_semantic_proof_status.json").exists()
    assert (ROOT / "docs/release/auth_lifecycle_semantic_proof_status.md").exists()
    assert status.status == "auth-lifecycle-controlled-semantic-proof-passing"


def test_auth_lifecycle_semantic_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_lifecycle_semantic_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_auth_lifecycle_semantic_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_auth_lifecycle_semantic_proof_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_lifecycle_semantic_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-lifecycle-semantic-proof-status:" in source
    assert "auth-lifecycle-semantic-proof-check:" in source
    assert "backend-implementation-2631-2670-full-check:" in source
