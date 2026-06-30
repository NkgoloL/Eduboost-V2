from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_route_logout_delegate import (
    build_status,
    ensure_auth_service_param,
    strip_malformed_auth_service_param_lines,
    write_status,
)

ROOT = Path(__file__).resolve().parents[2]


def test_syntax_rescue_removes_malformed_auth_service_param_line():
    broken = """async def logout(\n    response: Response,\n, auth_service: AuthApplicationService = Depends(get_auth_application_service)\n):\n    pass\n"""
    cleaned = strip_malformed_auth_service_param_lines(broken)
    assert ", auth_service:" not in cleaned


def test_multiline_signature_param_insertion_is_parseable():
    source = """async def logout(\n    response: Response\n):\n    return {\"ok\": True}\n"""
    repaired = ensure_auth_service_param(source, "logout")
    compile(repaired, "<test>", "exec")
    assert "auth_service: AuthApplicationService" in repaired
    assert "response: Response," in repaired


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
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_route_logout_delegate.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_auth_route_logout_delegate_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_auth_route_logout_delegate_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
