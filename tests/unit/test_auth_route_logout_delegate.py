from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from scripts.auth_route_logout_delegate import build_status, write_status
ROOT = Path(__file__).resolve().parents[2]

def test_logout_and_revoke_routes_delegate_to_service():
    status = build_status()
    assert status.status == "auth-route-logout-delegation-passing"

def test_logout_and_revoke_routes_have_no_direct_cookie_or_token_logic():
    status = build_status()
    for target in status.targets:
        assert target.direct_cookie_or_token_logic == []

def test_auth_route_logout_delegate_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/auth_route_logout_delegate_status.json").exists()
    assert (ROOT / "docs/release/auth_route_logout_delegate_status.md").exists()
    assert status.status == "auth-route-logout-delegation-passing"

def test_auth_route_logout_delegate_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run([sys.executable, "scripts/check_auth_route_logout_delegate.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}, check=False)
    assert result.returncode == 0, result.stdout

def test_auth_route_logout_delegate_registry_patcher_runs_directly():
    result = subprocess.run([sys.executable, "scripts/patch_auth_route_logout_delegate_registry.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    assert result.returncode == 0, result.stdout

def test_makefile_contains_auth_route_logout_delegate_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-route-logout-delegate-repair:" in source
    assert "auth-route-logout-delegate-check:" in source
    assert "backend-implementation-2551-2590-full-check:" in source
