from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.prod_frontend_runtime import (
    build_status,
    dockerfile_has_production_stage,
    dockerfile_has_standalone_copy,
    next_config_has_standalone_output,
    nginx_proxies_to_frontend,
    runtime_evidence_fields,
    write_status,
)


ROOT = Path(__file__).resolve().parents[2]


def test_dockerfile_frontend_runtime_contracts():
    text = (ROOT / "docker/Dockerfile.frontend").read_text(encoding="utf-8")

    assert dockerfile_has_production_stage(text)
    assert dockerfile_has_standalone_copy(text)


def test_next_config_has_standalone_output():
    candidates = [
        ROOT / "app/frontend/next.config.js",
        ROOT / "app/frontend/next.config.mjs",
        ROOT / "app/frontend/next.config.ts",
    ]
    text = ""
    for candidate in candidates:
        if candidate.exists():
            text = candidate.read_text(encoding="utf-8")
            break

    assert next_config_has_standalone_output(text)


def test_nginx_proxies_to_frontend_3050():
    text = (ROOT / "nginx/nginx.conf").read_text(encoding="utf-8")

    assert nginx_proxies_to_frontend(text)


def test_runtime_evidence_template_remains_pending_by_default():
    fields = runtime_evidence_fields()

    assert fields
    if any(not field.valid for field in fields):
        assert any(field.reason == "pending" for field in fields)


def test_prod_frontend_runtime_status_writes_reports():
    status = write_status()

    assert (ROOT / "docs/release/production_frontend_runtime_status.json").exists()
    assert (ROOT / "docs/release/production_frontend_runtime_status.md").exists()
    assert status.status in {
        "runtime-preflight-passing",
        "runtime-preflight-static-passing-compose-tool-unavailable",
        "runtime-preflight-not-proven",
        "runtime-evidence-accepted",
    }


def test_prod_frontend_runtime_local_status_has_no_static_blockers():
    status = build_status()
    static_blockers = [blocker for blocker in status.blockers if not blocker.startswith("runtime evidence:")]

    assert static_blockers == []


def test_prod_frontend_runtime_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_prod_frontend_runtime.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_prod_frontend_runtime_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_prod_frontend_runtime_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_prod_frontend_runtime_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "prod-frontend-runtime-repair:" in source
    assert "prod-frontend-runtime-check:" in source
    assert "backend-implementation-2471-2510-full-check:" in source
