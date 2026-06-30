from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_auth_http_success_scope_scripts_run():
    for command in [
        [sys.executable, "scripts/generate_auth_http_success_scope_report.py"],
        [sys.executable, "scripts/check_auth_http_success_scope.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, result.stdout


def test_auth_http_success_scope_report_exists():
    assert (ROOT / "docs/release/auth_http_success_scope_report.md").exists()
    assert (ROOT / "docs/release/auth_http_success_scope_report.json").exists()


def test_makefile_contains_auth_http_success_scope_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "auth-http-success-scope-report:" in text
    assert "auth-http-success-scope-check:" in text
    assert "backend-implementation-991-1030-full-check:" in text
