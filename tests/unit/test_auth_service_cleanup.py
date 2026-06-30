from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.auth_service_cleanup import build_status, monkey_patches, service_methods, write_status

ROOT = Path(__file__).resolve().parents[2]


def test_auth_application_service_has_no_monkey_patches():
    source = (ROOT / "app/services/auth_application_service.py").read_text(encoding="utf-8")
    assert monkey_patches(source) == []


def test_auth_application_service_exposes_required_methods():
    methods = service_methods()
    for method in ["register", "login", "refresh", "create_dev_session", "logout", "revoke_all_tokens"]:
        assert method in methods


def test_auth_service_cleanup_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/auth_service_cleanup_status.json").exists()
    assert (ROOT / "docs/release/auth_service_cleanup_status.md").exists()
    assert status.status in {
        "auth-service-cleanup-not-proven",
        "auth-service-monkeypatch-cleaned-route-delegation-pending",
        "auth-service-cleanup-passing",
    }


def test_auth_service_cleanup_has_no_hard_blockers_after_repair():
    status = build_status()
    hard = [b for b in status.blockers if "monkey-patches remain" in b or "missing" in b]
    assert hard == []


def test_auth_service_cleanup_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_auth_service_cleanup.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_auth_service_cleanup_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_auth_service_cleanup_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_auth_service_cleanup_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-service-cleanup-repair:" in source
    assert "auth-service-cleanup-check:" in source
    assert "backend-implementation-2511-2550-full-check:" in source


def test_legacy_auth_service_has_single_compat_access_token_store():
    source = (ROOT / "app/services/auth_service.py").read_text(encoding="utf-8")

    assert source.count("self._compat_access_tokens: dict[str, dict[str, str]] = {}") == 1
