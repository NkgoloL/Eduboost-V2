from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_route_service_dependency_repair import add_param, build_status, missing_auth_service_params, write_status

ROOT = Path(__file__).resolve().parents[2]


def test_add_auth_service_param_single_line_signature():
    source = """
from fastapi import Depends
async def logout(response: Response):
    return await auth_service.logout(response=response)
"""
    repaired = add_param(source, "logout")
    assert "auth_service: AuthApplicationService = Depends(get_auth_application_service)" in repaired


def test_add_auth_service_param_multi_line_signature():
    source = """
from fastapi import Depends
async def logout(
    response: Response
):
    return await auth_service.logout(response=response)
"""
    repaired = add_param(source, "logout")
    assert "response: Response," in repaired
    assert "auth_service: AuthApplicationService = Depends(get_auth_application_service)," in repaired


def test_auth_route_service_dependency_status_passing():
    assert build_status().status == "auth-route-service-dependencies-passing"


def test_no_auth_service_references_missing_param_remain():
    source = (ROOT / "app/api_v2_routers/auth.py").read_text(encoding="utf-8")
    assert missing_auth_service_params(source) == []


def test_auth_route_service_dependency_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/auth_route_service_dependency_repair_status.json").exists()
    assert (ROOT / "docs/release/auth_route_service_dependency_repair_status.md").exists()
    assert status.status == "auth-route-service-dependencies-passing"


def test_auth_route_service_dependency_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_route_service_dependencies.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_route_service_dependency_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-route-service-dependencies-repair:" in source
    assert "auth-route-service-dependencies-check:" in source
    assert "backend-implementation-2551-2590R3-full-check:" in source
