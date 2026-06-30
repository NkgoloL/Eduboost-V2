from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.prod_frontend_deployment import (
    build_status,
    certbot_uses_same_cert_mount,
    frontend_uses_production_target,
    has_frontend_service,
    nginx_cert_mount_aligned,
    nginx_depends_on_frontend,
    playwright_timeout_hardened,
    playwright_uses_next_port,
    write_status,
)


ROOT = Path(__file__).resolve().parents[2]


def test_production_compose_has_frontend_service_after_repair():
    text = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")

    assert has_frontend_service(text)
    assert frontend_uses_production_target(text)
    assert nginx_depends_on_frontend(text)


def test_nginx_and_certbot_certificate_mounts_are_aligned():
    text = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")

    assert nginx_cert_mount_aligned(text)
    assert certbot_uses_same_cert_mount(text)


def test_playwright_default_matches_next_port():
    text = (ROOT / "playwright.config.ts").read_text(encoding="utf-8")

    assert playwright_uses_next_port(text)
    assert playwright_timeout_hardened(text)


def test_production_frontend_deployment_status_writes_reports():
    status = write_status()

    assert (ROOT / "docs/release/production_frontend_deployment_status.json").exists()
    assert (ROOT / "docs/release/production_frontend_deployment_status.md").exists()
    assert status.status == "production-frontend-configured"


def test_production_frontend_deployment_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_prod_frontend_deployment.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_production_frontend_deployment_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_prod_frontend_deployment_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_production_frontend_deployment_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "prod-frontend-deployment-repair:" in source
    assert "prod-frontend-deployment-check:" in source
    assert "backend-implementation-2431-2470-full-check:" in source


def test_production_frontend_deployment_status_builder_is_passing():
    status = build_status()

    assert status.status == "production-frontend-configured"
    assert not status.blockers
